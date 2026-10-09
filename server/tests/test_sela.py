"""Sela's Crew deck (plans/base-game.md Step 10): every operation, his missions, Cadet Training and random games.
Specs: resources/scans/base_game/cards/captains/sela/ and resources/scans/base_game/boards/cb-sela-*.md."""

import random

import pytest

from engine import cards as registry
from engine.content import content
from engine.game import advance, choose, hand_size
from engine.ops import _payable_developments, Ctx
from engine.scoring import score_player
from engine.setup import SeatSetup, new_game
from engine.state import OpRef
from engine.views import game_view
from tests.scenario import activate, answer, can_play, card, given, options, play
from tests.test_market_cards import RICH, finish

CARDS = content().cards
DECK = content().crew_deck("sela")
OWN = sorted(c.id for c in DECK if not c.same_as)  # the copies (Utilize, Recruit, ...) are tested with the originals


def me(s):
    return s.players[0]


def opp(s):
    return s.players[1]


def refresh(s):
    s.decision = None
    advance(s, flag_irreversible=False)


def sela(**kw):
    return given(deck="sela", opponent="soval", **kw)


def goraxus(s):
    return card(s, "1SEL02", zone="fleet")


def zone_for(cid):
    return {"Person": "duty", "Location": "locations"}.get(CARDS[cid].suit, "fleet")


def can_activate(s, inst, index):
    return f"activate:{inst.uid}:{index}" in {o.id for o in s.decision.options}


def run(s, inst, index, event=None):
    s.decision = None
    s.op_queue.append(OpRef(mode="trigger" if event else "auto", seat=0, uid=inst.uid, index=index, event=event))
    advance(s, flag_irreversible=False)


def developments(s):
    return [i.card for i in _payable_developments(Ctx(s, OpRef(mode="auto", seat=0)))]


# ------------------------------------------------------------------ the deck as a whole

def test_setup_and_copies():
    s = sela()
    p = me(s)
    assert p.captain.card == "1SEL01" and p.away_pool == 4 and [i.card for i in p.fleet] == ["1SEL02"]
    assert len(p.development) == 6 and len(p.reserve) == 6
    assert sorted(i.card for i in p.discard) == ["1SEL22", "1SEL23", "1SEL24"]  # Utilize, I.R.W. Terix, Remans
    assert len(p.hand) + len(p.draw) == 7
    assert registry.OPS[("1SEL21", 0)].fn is registry.OPS[("2KHA09", 0)].fn  # Infiltrate
    assert registry.OPS[("1SEL08", 0)].fn is registry.OPS[("2CAR06", 0)].fn and "1SEL08" in registry.DUTY_SLOTS
    assert "1SEL21" not in registry.DEV_COSTS and "1SEL08" in registry.DEV_COSTS
    for c in DECK:
        for index, op in enumerate(c.operations):
            assert registry.has_code(c.id, index, op.kind), (c.id, c.name, index, op.kind)


NEEDS_OWN_SETUP = {
    ("1SEL07", 3),  # needs the Scimitar at a neutral Location with 9 Military: covered below
    ("1SEL01", 1),  # needs Infiltrate or Conquer in hand
}
NEEDS_OWN_SETUP = {("1SEL14", 2)}  # Tomalak: needs an Attack in the Discard pile


@pytest.mark.parametrize("cid,index", [(cid, i) for cid in OWN for i, op in enumerate(CARDS[cid].operations)
                                       if op.kind in ("PLAY", "ACTIVATION") and (cid, i) in registry.OPS])
def test_every_sela_operation_runs(cid, index):
    if (cid, index) in NEEDS_OWN_SETUP:
        pytest.skip("covered by its own test")
    kind = CARDS[cid].operations[index].kind
    tracks = {"research": 9, "influence": 9, "military": 9}
    if kind == "PLAY":
        position = {**RICH, "hand": RICH["hand"] + [cid, "1SEL16", "1SEL15"], "tracks": tracks, "dilithium": 12,
                    "locations": ["2LOC07"]}  # a Romulan and an Attack to discard
    else:
        z = zone_for(cid)
        position = {**RICH, z: [cid] if z == "duty" else RICH.get(z, []) + [cid], "tracks": tracks,
                    "hand": RICH["hand"] + ["1SEL21", "1SEL16", "1SEL24"], "dilithium": 12,  # Infiltrate, a Romulan, a Reman
                    "locations": RICH.get("locations", []) + ([] if z == "locations" else ["2LOC07"])}
        if z == "locations":
            position["locations"] = [cid, "2LOC07"]
    for seed in range(2):
        s = sela(**position)
        for ship in me(s).fleet:
            ship.at = s.neutral[0].uid
        for loc in me(s).locations:
            loc.away[0] = 1
        refresh(s)
        inst = card(s, cid, zone="hand" if kind == "PLAY" else zone_for(cid))
        if kind == "PLAY":
            assert can_play(s, inst, index), f"{cid} {index} not playable"
            play(s, inst, index)
        else:
            assert can_activate(s, inst, index), f"{cid} {index} not offered"
            activate(s, inst, index)
        finish(s, seed)


@pytest.mark.parametrize("seed", range(6))
def test_random_games_with_sela(seed):
    rng = random.Random(seed)
    other = ["soval", "kirk", "sisko", "picard", "shran", "koloth"][seed]
    s = new_game(seed, "two_player", [SeatSetup("P", "sela", "advanced" if seed % 2 else "basic"),
                                      SeatSetup("O", other, "basic")], [], False, box="both")
    advance(s, flag_irreversible=False)
    for n in range(6000):
        if s.step == "over":
            break
        ids = [o.id for o in s.decision.options]
        plays = [i for i in ids if i.startswith(("play:", "activate:", "mission:"))]
        choose(s, s.decision.seat, rng.choice(plays) if plays and rng.random() < 0.85 else rng.choice(ids),
               flag_irreversible=False)
        if n % 80 == 0:
            game_view(s, 0)
    assert s.step == "over"


def test_cadet_training_with_sela():
    s = new_game(2, "cadet", [SeatSetup("P", "sela", "advanced")], [], False, box="core")
    advance(s, flag_irreversible=False)
    rng = random.Random(2)
    for _ in range(4000):
        if s.step == "over":
            break
        ids = [o.id for o in s.decision.options]
        plays = [i for i in ids if i.startswith(("play:", "activate:", "mission:"))]
        choose(s, 0, rng.choice(plays) if plays and rng.random() < 0.85 else rng.choice(ids), flag_irreversible=False)
    assert s.step == "over"


# ------------------------------------------------------------------ the Captain and her Developments

def complete(s, mission_id):
    choose(s, 0, f"mission:{mission_id}", flag_irreversible=False)


def offered(s, mission_id):
    return f"mission:{mission_id}" in {o.id for o in s.decision.options}


def drive(s, *prefer):
    """Answer until the Action Step menu: use offered Reactions, then the first preferred option, else the first."""
    while s.decision.kind != "action":
        opts = options(s)
        pick = next((o for o in opts if o.startswith("Use")), None) or next((o for p in prefer for o in opts if p in o), None)
        answer(s, pick or opts[0])


def test_sela_is_paid_after_every_attack_even_an_ignored_one():
    s = sela(hand=["1SEL06"], empty_hand=True)  # Shinzon: your opponent takes an Incident
    latinum = me(s).latinum
    play(s, card(s, "1SEL06", zone="hand"), 0)
    drive(s, "1 Latinum", "No")
    assert me(s).latinum == latinum + 1
    s = sela(hand=["1SEL06"], empty_hand=True, opp={"duty": ["2PER16"], "hand": ["2PER15"]})  # Riva ignores it
    latinum, incidents = me(s).latinum, len(s.incident)
    play(s, card(s, "1SEL06", zone="hand"), 0)
    while s.decision.kind != "action":
        opts = options(s)
        answer(s, next((o for o in opts if o.startswith("Use") or "1 Latinum" in o), "No" if "No" in opts else opts[0]))
    assert me(s).latinum == latinum + 1 and len(s.incident) == incidents


def test_sela_scans_by_discarding_infiltrate_or_conquer():
    s = sela(hand=["1SEL21"], empty_hand=True, latinum=3)
    activate(s, me(s).captain, 1)
    finish(s)
    assert me(s).discard[-1].card != "" and any(i.card == "1SEL21" for i in me(s).discard)
    without = sela(hand=["2PER16"], empty_hand=True, latinum=3)
    assert not can_activate(without, me(without).captain, 1)


def test_sela_scores_attacks_that_are_not_romulan_or_reman():
    s = sela()
    base = registry.ENDGAME["1SEL01"](s, me(s))
    me(s).discard.extend(s.new_inst(c) for c in ("2PER06", "1SEL14"))  # Harry Mudd counts; Tomalak is Romulan
    assert registry.ENDGAME["1SEL01"](s, me(s)) == base + 1


def test_forced_singularity_costs_a_deployed_ship():
    s = sela()
    assert "1SEL08" in developments(s)
    me(s).fleet.clear()
    assert "1SEL08" not in developments(s)


def test_scimitar_needs_a_romulan_and_remus():
    s = sela(hand=["1SEL07", "2PER16"], empty_hand=True, locations=["1SEL19"])
    play(s, card(s, "1SEL07", zone="hand"), 0)
    drive(s)
    assert any(i.card == "1SEL07" for i in me(s).fleet)
    assert [b.card for b in card(s, "1SEL19", zone="locations").beamed] == ["2PER16"]
    s = sela(hand=["1SEL07", "2PER16"], empty_hand=True)  # no Remus
    play(s, card(s, "1SEL07", zone="hand"), 0)
    drive(s)
    assert not any(i.card == "1SEL07" for i in me(s).fleet)


def test_scimitar_logs_an_opponent_location_and_takes_a_neutral_one():
    s = sela(fleet=["1SEL07"], tracks={"military": 7}, opp={"locations": ["2LOC08"]})  # Indri VIII: two Skill icons
    glory = me(s).glory
    activate(s, card(s, "1SEL07", zone="fleet"), 2)
    answer(s, "Indri VIII")  # Soval also controls Vulcan
    drive(s, "1 Latinum")
    assert any(i.card == "2LOC08" for i in opp(s).log) and [i.card for i in opp(s).locations] == ["2SOV03"]
    assert me(s).glory == glory + 2 and any(i.card == "1SEL07" for i in me(s).discard)
    s = sela(fleet=["1SEL07"], tracks={"military": 9})
    loc = s.neutral[0]
    card(s, "1SEL07", zone="fleet").at = loc.uid
    refresh(s)
    activate(s, card(s, "1SEL07", zone="fleet"), 3)
    drive(s)
    assert any(i.uid == loc.uid for i in me(s).locations)


def test_donatra_keeps_drawn_cards_for_dilithium():
    s = sela(hand=["1SEL04"], empty_hand=True, dilithium=2)
    dilithium = me(s).dilithium
    play(s, card(s, "1SEL04", zone="hand"), 0)
    answer(s, "Yes")
    answer(s, "No")
    answer(s, "No")
    drive(s)
    assert me(s).dilithium == dilithium - 1 and len(me(s).hand) == 1


# ------------------------------------------------------------------ the rest of the deck

def test_tomalak_dismisses_starfleet_duty_officers():
    s = sela(hand=["1SEL14"], empty_hand=True, dilithium=2, opp={"duty": ["2PER11"]})  # Malcolm Reed
    assert "Starfleet" in CARDS["2PER11"].traits
    hand = len(opp(s).hand)
    play(s, card(s, "1SEL14", zone="hand"), 0)
    drive(s, "1 Dilithium")
    assert not opp(s).duty and len(opp(s).hand) == hand - 1


def test_trul_is_paid_when_a_cloak_is_put_into_play():
    s = sela(duty=["1SEL16"], hand=["1SEL17"], empty_hand=True)
    latinum = me(s).latinum
    play(s, card(s, "1SEL17", zone="hand"), 0)  # I.R.W. Khazara
    drive(s, "No")
    assert me(s).latinum == latinum + 1 and any(i.card == "1SEL17" for i in me(s).fleet)


def test_warbirds_send_a_team_past_opponent_ships():
    s = sela(hand=["1SEL17"], empty_hand=True, opp={"fleet": ["2SHI01"]})
    for loc in s.neutral:
        loc.away.clear()
    s.neutral[:] = s.neutral[:1]
    card(s, "2SHI01", seat=1, zone="fleet").at = s.neutral[0].uid
    refresh(s)
    play(s, card(s, "1SEL17", zone="hand"), 0)
    answer(s, "Yes")
    drive(s)
    assert s.neutral[0].away.get(0) == 1 or any(loc.away.get(0) for loc in me(s).locations)


def test_remus_makes_the_opponent_discard_and_pays_for_remans():
    s = sela(hand=["1SEL19"], empty_hand=True)
    hand = len(opp(s).hand)
    play(s, card(s, "1SEL19", zone="hand"), 0)
    drive(s, "1 Dilithium")
    assert len(opp(s).hand) == hand - 1 and any(i.card == "1SEL19" for i in me(s).locations)
    s = sela(locations=["1SEL19"], hand=["1SEL24"], empty_hand=True)
    dilithium = me(s).dilithium
    run(s, card(s, "1SEL19", zone="locations"), 2)
    answer(s, "Yes")
    assert me(s).dilithium == dilithium + 3


def test_remans_log_themselves_or_let_the_opponent_draw():
    s = sela(hand=["1SEL24", "2PER16"], empty_hand=True)
    play(s, card(s, "1SEL24", zone="hand"), 0)
    while "Remans" not in s.decision.prompt:
        answer(s, options(s)[0])
    answer(s, "Log this card")
    assert me(s).log[-1].card == "1SEL24" and me(s).draw[0].card == "2PER16"


def test_movar_draws_for_shady_cards():
    s = sela(duty=["1SEL18"], staging=["2PER06", "2PER10"], empty_hand=True)  # Harry Mudd and Lursa are Shady
    run(s, card(s, "1SEL18", zone="duty"), 1)
    assert len(me(s).hand) == 1  # Sela herself is Shady too: three Shady, one card


def test_tpel_triggers_a_control_operation():
    s = sela(hand=["1SEL12"], empty_hand=True, locations=["2LOC07"], latinum=1, tracks={"influence": 4})
    dilithium = me(s).dilithium
    play(s, card(s, "1SEL12", zone="hand"), 0)
    drive(s)
    assert me(s).dilithium == dilithium + 3 and len(me(s).hand) == 1  # Dozaria: gain 3 Dilithium
    assert hand_size(sela(duty=["1SEL12"]), me(sela(duty=["1SEL12"]))) == 6


# ------------------------------------------------------------------ missions

def test_romulan_might():
    s = sela(tracks={"influence": 6, "military": 5})
    assert not offered(s, "romulan-might")
    s = sela(tracks={"influence": 6, "military": 6}, dilithium=5)
    assert offered(s, "romulan-might")
    developments_before = len(me(s).development)
    complete(s, "romulan-might")
    finish(s)
    assert len(me(s).development) == developments_before - 1 and "romulan-might" in me(s).missions_completed


def test_the_reunification_plot():
    s = sela(board="advanced", staging=["2PER21", "2SHI03", "1CAR08", "1PER21"])  # Talok, D'Kyr, Lirpa, Sakonna
    hand = len(me(s).hand)
    complete(s, "the-reunification-plot")
    drive(s, "No")
    assert me(s).tracks["influence"] == 3 and len(me(s).hand) == hand + 1  # Sela herself is the one Shady


def test_the_duras_plot_counts_a_turn_long_cloak():
    """KW-TREAT-05: a Ship given Cloak for the turn is a Ship that has Cloak."""
    s = sela(board="advanced")
    goraxus(s).beamed.append(s.new_inst("2PER10"))  # Lursa, a Klingon, on the cloaked Goraxus
    refresh(s)
    assert offered(s, "the-duras-plot")
    glory = me(s).glory
    complete(s, "the-duras-plot")
    drive(s, "Goraxus")
    assert me(s).tracks["military"] == 1 and me(s).glory == glory + 2
    assert not me(s).fleet and any(i.card == "2PER10" for i in me(s).discard)
    plain = sela(board="advanced", fleet=["2SHI01"])
    me(plain).fleet[:] = [i for i in me(plain).fleet if i.card == "2SHI01"]
    probe = card(plain, "2SHI01", zone="fleet")
    probe.beamed.append(plain.new_inst("2PER10"))
    refresh(plain)
    assert not offered(plain, "the-duras-plot")
    plain.turn_traits[probe.uid] = ["Cloak"]
    refresh(plain)
    assert offered(plain, "the-duras-plot")


def test_tomalak_draws_an_attack_from_the_discard_pile():
    s = sela(duty=["1SEL14"], hand=["2PER16"], empty_hand=True, discard=["2PER06"])
    activate(s, card(s, "1SEL14", zone="duty"), 2)
    drive(s)
    assert [i.card for i in me(s).hand] == ["2PER06"]
    bare = sela(duty=["1SEL14"], hand=["2PER16"], empty_hand=True)
    me(bare).discard[:] = [i for i in me(bare).discard if "Attack" not in CARDS[i.card].traits]
    refresh(bare)
    assert not can_activate(bare, card(bare, "1SEL14", zone="duty"), 2)
