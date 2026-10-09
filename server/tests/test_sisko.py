"""Sisko's Crew deck (plans/base-game.md Step 11): every operation, his missions, Cadet Training and random games.
Specs: resources/scans/base_game/cards/captains/sisko/ and resources/scans/base_game/boards/cb-sisko-*.md."""

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
DECK = content().crew_deck("sisko")
OWN = sorted(c.id for c in DECK if not c.same_as)  # the copies (Utilize, Recruit, ...) are tested with the originals


def me(s):
    return s.players[0]


def opp(s):
    return s.players[1]


def refresh(s):
    s.decision = None
    advance(s, flag_irreversible=False)


def sisko(**kw):
    return given(deck="sisko", opponent="soval", **kw)


def ds9(s):
    return card(s, "1SIS03", zone="fleet")


def bajor(s):
    return card(s, "1SIS02", zone="locations")


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
    s = sisko()
    p = me(s)
    assert p.captain.card == "1SIS01" and p.away_pool == 6
    assert [i.card for i in p.fleet] == ["1SIS03"] and [i.card for i in p.locations] == ["1SIS02"]
    assert len(p.development) == 7 and len(p.reserve) == 5 and len(p.hand) + len(p.draw) == 10
    assert registry.OPS[("1SIS17", 0)].fn is registry.OPS[("2GEO18", 0)].fn  # Utilize
    assert "1SIS03" in registry.CANNOT_WARP and "1SIS13" in registry.CANNOT_PROMOTE
    assert not CARDS["1SIS05"].operations or all(op.kind == "DEVELOPMENT COST" for op in CARDS["1SIS05"].operations)
    for c in DECK:
        for index, op in enumerate(c.operations):
            assert registry.has_code(c.id, index, op.kind), (c.id, c.name, index, op.kind)


NEEDS_OWN_SETUP = {
    ("1SIS04", 0),  # needs an exhausted Bajoran
    ("1SIS01", 1),  # needs a Location with Starfleet/Starbase
    ("1SIS10", 2),  # needs an opponent Away Team at a neutral Location
}


@pytest.mark.parametrize("cid,index", [(cid, i) for cid in OWN for i, op in enumerate(CARDS[cid].operations)
                                       if op.kind in ("PLAY", "ACTIVATION") and (cid, i) in registry.OPS])
def test_every_sisko_operation_runs(cid, index):
    if (cid, index) in NEEDS_OWN_SETUP:
        pytest.skip("covered by its own test")
    kind = CARDS[cid].operations[index].kind
    tracks = {"research": 9, "influence": 9, "military": 9}
    if kind == "PLAY":
        position = {**RICH, "hand": RICH["hand"] + [cid, "2SHI01"], "tracks": tracks, "dilithium": 12,
                    "locations": ["2LOC07"]}  # a Ship in hand
    else:
        z = zone_for(cid)
        position = {**RICH, z: [cid] if z == "duty" else RICH.get(z, []) + [cid], "tracks": tracks,
                    "hand": RICH["hand"] + ["2SHI01"], "dilithium": 12,  # a Ship
                    "locations": RICH.get("locations", []) + ([] if z == "locations" else ["2LOC07"])}
        if z == "locations":
            position["locations"] = [cid, "2LOC07"]
    for seed in range(2):
        s = sisko(**position)
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
def test_random_games_with_sisko(seed):
    rng = random.Random(seed)
    other = ["soval", "kirk", "sela", "picard", "shran", "koloth"][seed]
    s = new_game(seed, "two_player", [SeatSetup("P", "sisko", "advanced" if seed % 2 else "basic"),
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


def test_cadet_training_with_sisko():
    s = new_game(2, "cadet", [SeatSetup("P", "sisko", "advanced")], [], False, box="core")
    advance(s, flag_irreversible=False)
    rng = random.Random(2)
    for _ in range(4000):
        if s.step == "over":
            break
        ids = [o.id for o in s.decision.options]
        plays = [i for i in ids if i.startswith(("play:", "activate:", "mission:"))]
        choose(s, 0, rng.choice(plays) if plays and rng.random() < 0.85 else rng.choice(ids), flag_irreversible=False)
    assert s.step == "over"


# ------------------------------------------------------------------ the Captain and his starting cards

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


def test_sisko_gains_dilithium_for_taking_control_and_scores_locations():
    s = sisko(hand=["1SIS21"], empty_hand=True)
    dilithium = me(s).dilithium
    play(s, card(s, "1SIS21", zone="hand"), 0)  # The Wormhole
    drive(s, "No", "Top")
    assert registry.ENDGAME["1SIS01"](s, me(s)) == 2 and any(i.card == "1SIS21" for i in me(s).locations)
    assert me(s).dilithium == dilithium + 2  # playing a Crew Location is taking control (KW-TC-02)
    s = sisko()
    loc = s.neutral[0]
    loc.away[0] = 3
    from engine.game import take_control

    dilithium = me(s).dilithium
    take_control(s, me(s), loc, run_control=False)
    refresh(s)
    drive(s)
    assert me(s).dilithium == dilithium + 2


def test_sisko_sends_an_away_team_only_to_starfleet_or_starbase():
    s = sisko()
    assert not can_activate(s, me(s).captain, 1)  # Bajor is neither, and Deep Space 9 is a Ship
    s = sisko(locations=["1SIS02", "1SIS07"])  # Starbase 375
    activate(s, me(s).captain, 1)
    drive(s)
    assert card(s, "1SIS07", zone="locations").away.get(0, 0) == 1 and bajor(s).away.get(0, 0) == 0


def test_deep_space_9_cannot_warp_and_holds_cards():
    s = sisko(hand=["2PER16", "2PER17"], empty_hand=True)
    station = ds9(s)
    assert not any("warp" in o.lower() and "Deep Space 9" in o for o in options(s))
    activate(s, station, 1)
    drive(s)
    assert len(ds9(s).beamed) == 1 and len(me(s).hand) == 0
    ds9(s).exhausted = False
    me(s).hand.append(s.new_inst("2CAR07"))
    refresh(s)
    activate(s, ds9(s), 1)  # the only card in hand pays the cost, so only the recall is left
    drive(s)
    assert not ds9(s).beamed and len(me(s).hand) == 1
    empty = sisko(empty_hand=True)
    refresh(empty)
    assert not can_activate(empty, ds9(empty), 1)  # nothing to discard


def test_bajor_draws_for_away_teams():
    s = sisko(empty_hand=True)
    bajor(s).away[0] = 3
    refresh(s)
    activate(s, bajor(s), 0)
    assert len(me(s).hand) == 2


# ------------------------------------------------------------------ Developments

def test_orb_of_prophecy_reduces_a_development_by_one_of_each():
    s = sisko(hand=["1SIS04", "2PER16"], empty_hand=True)
    me(s).dilithium, me(s).latinum, me(s).glory = 2, 2, 0
    assert "1SIS05" not in developments(s)  # Orb of the Emissary costs 3 Dilithium and 3 Latinum
    play(s, card(s, "1SIS04", zone="hand"), 2)
    answer(s, "Orb of the Emissary")
    drive(s)
    assert (me(s).dilithium, me(s).latinum) == (0, 0) and me(s).draw[0].card == "1SIS05"
    assert me(s).log[-1].card == "1SIS04"


def test_self_replicating_mines_absorb_an_attack_and_are_logged():
    s = sisko(fleet=["1SIS06"], opp={"hand": ["1SHI08"]})  # Son'a Battlecruiser: steal 1 Dilithium
    s.active = 1
    s.step = "action"
    refresh(s)
    dilithium = me(s).dilithium
    choose(s, 1, f"play:{card(s, '1SHI08', seat=1, zone='hand').uid}:0", flag_irreversible=False)
    while s.decision is not None and s.decision.kind != "action":
        answer(s, options(s)[0])
    assert me(s).dilithium == dilithium and me(s).log[-1].card == "1SIS06" and not any(i.card == "1SIS06" for i in me(s).fleet)


def test_self_replicating_mines_come_back_when_the_opponent_gains_military():
    s = sisko(fleet=["1SIS06"])
    from engine.ops import Actions

    acts = Actions(Ctx(s, OpRef(mode="auto", seat=1)), ["GAIN_SPECIALTY"])
    for _ in acts.gain_specialty("military", 1):
        pass
    refresh(s)
    drive(s)
    assert any(i.card == "1SIS06" for i in me(s).hand)


def test_garak_chooses_two_of_three():
    s = sisko(hand=["1SIS09"], empty_hand=True, opp={"duty": ["2PER16"]})
    play(s, card(s, "1SIS09", zone="hand"), 0)
    answer(s, "Dismiss an opponent")
    if any("Riva" in o for o in options(s)):
        answer(s, "Do not use")
    drive(s, "Gain 1 Influence")
    assert not opp(s).duty and me(s).tracks["influence"] == 1 and len(me(s).hand) == 1
    assert hand_size(sisko(duty=["1SIS09"]), me(sisko(duty=["1SIS09"]))) == 7


def test_worf_son_of_mogh_is_dismissed_to_ignore_an_attack():
    s = sisko(duty=["1SIS10"], opp={"hand": ["1SHI08"]})
    s.active = 1
    s.step = "action"
    refresh(s)
    dilithium = me(s).dilithium
    choose(s, 1, f"play:{card(s, '1SHI08', seat=1, zone='hand').uid}:0", flag_irreversible=False)
    while s.decision is not None and s.decision.kind != "action":
        opts = options(s)
        answer(s, next((o for o in opts if "Worf" in o), opts[0]))
    assert me(s).dilithium == dilithium and not me(s).duty


# ------------------------------------------------------------------ the rest of the deck

def test_miles_obrien_cannot_be_promoted_and_refits_a_ship():
    s = sisko(hand=["1SIS13"], empty_hand=True, discard=["2SHI01"], dilithium=1, tracks={"military": 5})
    play(s, card(s, "1SIS13", zone="hand"), 1)
    drive(s, "No")
    assert any(i.card == "2SHI01" for i in me(s).fleet)
    s = sisko(hand=["1SIS13"], empty_hand=True)
    activate(s, ds9(s), 2)
    drive(s)
    assert not me(s).duty and [i.card for i in me(s).hand] == ["1SIS13"]  # the promotion does nothing
    poor = sisko(hand=["1SIS13"], empty_hand=True, discard=["2SHI01"], tracks={"military": 5})
    me(poor).dilithium = me(poor).glory = 0
    refresh(poor)
    assert not can_play(poor, card(poor, "1SIS13", zone="hand"), 1)


def test_odo_logs_a_shady_person_for_glory():
    s = sisko(duty=["1SIS14"], hand=["2PER06"], empty_hand=True)  # Harry Mudd is Shady
    glory = me(s).glory
    activate(s, card(s, "1SIS14", zone="duty"), 1)
    drive(s)
    assert me(s).glory == glory + 1 and me(s).log[-1].card == "2PER06" and len(me(s).hand) == 1


def test_defiant_makes_an_opponent_at_its_location_discard_two():
    s = sisko(hand=["1SIS15"], empty_hand=True, opp={"fleet": ["2SHI01"]})
    target = s.neutral[0]
    for ship in opp(s).fleet:
        ship.at = target.uid
    s.neutral[:] = [target]
    me(s).locations.clear()
    refresh(s)
    hand = len(opp(s).hand)
    play(s, card(s, "1SIS15", zone="hand"), 0)
    drive(s)
    assert len(opp(s).hand) == hand - 2


def test_jadzia_dax_scans_instead_of_gaining():
    s = sisko(duty=["1SIS22"], hand=["2GEO16", "2PER16"], empty_hand=True)  # Recruit: gain a Person
    deck = len(s.market_decks["Person"])
    play(s, card(s, "2GEO16", zone="hand"), 0)
    seen = False
    while s.decision.kind != "action":
        opts = options(s)
        seen = seen or any("Jadzia Dax" in o for o in opts)
        answer(s, next((o for o in opts if "Jadzia Dax" in o), opts[0]))
    assert seen and len(s.market_decks["Person"]) <= deck


def test_kira_finds_the_people_of_bajor_and_is_promoted():
    s = sisko(hand=["1SIS23"], empty_hand=True, opp={"duty": ["1PER09"]})  # Joret Dal is Cardassian
    play(s, card(s, "1SIS23", zone="hand"), 0)
    while s.decision.kind != "action":
        opts = options(s)
        answer(s, next((o for o in opts if "Do not use" in o), opts[0]))
    assert [i.card for i in me(s).duty] == ["1SIS23"] and any(i.card == "1SIS12" for i in me(s).hand)
    assert not opp(s).duty
    s = sisko(hand=["1SIS23"], empty_hand=True)
    theirs = opp(s).tracks["influence"]
    play(s, card(s, "1SIS23", zone="hand"), 1)
    assert me(s).tracks["military"] == 3 and opp(s).tracks["influence"] == theirs + 1


def test_kira_reacts_when_the_opponent_takes_control():
    s = sisko(duty=["1SIS23"], empty_hand=True)
    from engine.game import take_control

    dilithium = me(s).dilithium
    take_control(s, opp(s), s.neutral[0], run_control=False)
    refresh(s)
    drive(s)
    assert me(s).dilithium == dilithium + 1 and len(me(s).hand) == 1


def test_worf_removes_an_opponent_away_team():
    s = sisko(duty=["1SIS10"])
    assert not can_activate(s, card(s, "1SIS10", zone="duty"), 2)
    s.neutral[0].away[1] = 2
    refresh(s)
    glory = me(s).glory
    activate(s, card(s, "1SIS10", zone="duty"), 2)
    while s.decision.kind != "action":
        opts = options(s)
        answer(s, next((o for o in opts if "Do not use" in o), opts[0]))
    assert s.neutral[0].away[1] == 1 and me(s).glory == glory + 1


def test_starbase_375_free_plays_a_person_after_a_ship():
    s = sisko(locations=["1SIS02", "1SIS07"], hand=["1SIS25", "1SIS13"], empty_hand=True)
    play(s, card(s, "1SIS25", zone="hand"), 0)  # U.S.S. Rio Grande
    drive(s, "Draw 2")
    assert any(i.card == "1SIS13" for i in me(s).staging) and me(s).actions == 2
    assert card(s, "1SIS07", zone="locations").exhausted


def test_the_wormhole_reorders_the_location_deck():
    s = sisko(hand=["1SIS21"], empty_hand=True)
    top = [i.uid for i in s.location_deck[:3]]
    play(s, card(s, "1SIS21", zone="hand"), 0)
    drive(s, "No", "Bottom")
    assert sorted(i.uid for i in s.location_deck[-3:]) == sorted(top)


def test_bashir_chooses_two_of_four():
    s = sisko(duty=["1SIS08"], hand=["2INC01"], empty_hand=True, dilithium=1)
    incidents = len(s.incident)
    activate(s, card(s, "1SIS08", zone="duty"), 1)
    answer(s, "Find Miles O'Brien")
    drive(s, "Return an Incident")
    assert any(i.card == "1SIS13" for i in me(s).hand) and len(s.incident) == incidents + 1
    assert not any(content().cards[i.card].suit == "Incident" for i in me(s).hand)


def test_quark_resupply_counts_ferengi():
    from engine.ops import start

    for duty, gain in ((["1SIS24"], 1), (["1SIS24", "2PER16"], 1)):
        s = sisko(duty=duty)
        quark = card(s, "1SIS24", zone="duty")
        latinum = me(s).latinum
        start(s, OpRef(mode="op", seat=0, uid=quark.uid, card="1SIS24", index=1))
        ferengi = sum(1 for i in Ctx(s, OpRef(mode="auto", seat=0)).in_play() if "Ferengi" in content().cards[i.card].traits)
        assert me(s).latinum == latinum + (2 if ferengi >= 2 else 1)


def test_quark_is_paid_for_an_operation_with_a_latinum_cost():
    s = sisko(duty=["1SIS24"], hand=["1ALL08"], empty_hand=True, latinum=2, tracks={"military": 3})
    glory = me(s).glory
    play(s, card(s, "1ALL08", zone="hand"), 1)  # Karemma: spend 2 Latinum to gain an Action
    drive(s)
    assert me(s).glory == glory + 1
    s = sisko(duty=["1SIS24"], hand=["1SIS04", "2PER16"], empty_hand=True)
    me(s).dilithium, me(s).latinum, me(s).glory = 5, 5, 0
    refresh(s)
    play(s, card(s, "1SIS04", zone="hand"), 2)  # enlist Garak for 2 Latinum, less 1
    answer(s, "Garak")
    assert s.decision.kind == "action" and me(s).glory == 0 and me(s).latinum == 4  # a development cost is not one
    s = sisko(duty=["1SIS24"], hand=["1ALL07"], empty_hand=True)
    glory = me(s).glory
    play(s, card(s, "1ALL07", zone="hand"), 0)  # Halkan Council: no cost
    assert s.decision.kind == "action" and me(s).glory == glory


def test_rio_grande_shares_the_shuttlecraft_play():
    assert registry.OPS[("1SIS25", 1)].fn is registry.OPS[("1PIC14", 1)].fn
    s = sisko(hand=["1SIS25"], empty_hand=True)
    dilithium = me(s).dilithium
    play(s, card(s, "1SIS25", zone="hand"), 1)
    drive(s, "Neither")
    assert me(s).dilithium == dilithium + 1


# ------------------------------------------------------------------ missions

def test_a_call_to_arms_discounts_a_development_per_starbase():
    s = sisko(fleet=["2SHI01", "2SHI03", "1SIS15"], tracks={"military": 7})
    me(s).dilithium, me(s).latinum, me(s).glory = 1, 0, 0
    assert offered(s, "a-call-to-arms")  # Deep Space 9 and three more Ships
    complete(s, "a-call-to-arms")
    answer(s, "Julian Bashir")  # 2 Dilithium, 1 less for the one Starbase in play (Deep Space 9)
    drive(s)
    assert me(s).dilithium == 0 and me(s).draw[0].card == "1SIS08"
    few = sisko(fleet=["2SHI01", "2SHI03"], tracks={"military": 7})
    assert not offered(few, "a-call-to-arms")


def test_bajors_application_to_the_federation():
    s = sisko(board="advanced", staging=["1SIS13", "1SIS08", "1SIS12", "1SIS23"], fleet=["2SHI01"])
    # O'Brien and Bashir are Starfleet; Bajor, People of Bajor and Kira are Bajoran
    assert not offered(s, "bajors-application-to-the-federation")  # no Ship at Bajor yet
    card(s, "2SHI01", zone="fleet").at = bajor(s).uid
    bajor(s).exhausted = True
    refresh(s)
    complete(s, "bajors-application-to-the-federation")
    drive(s)
    assert not bajor(s).exhausted and "bajors-application-to-the-federation" in me(s).missions_completed


def test_contacting_the_dominion():
    s = sisko(board="advanced", staging=["1SIS14", "1PER10", "1ALL08"])  # Odo, Laas, Karemma
    hand = len(me(s).hand)
    complete(s, "contacting-the-dominion")
    drive(s)
    assert me(s).tracks["influence"] == 3 and len(me(s).hand) >= hand + 2
    assert score_player(s, me(s))["parts"]["missions"] == 3
