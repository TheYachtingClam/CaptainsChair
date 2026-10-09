"""Picard's Crew deck (plans/base-game.md Step 7): every operation, his missions, Cadet Training and random games.
Specs: resources/scans/base_game/cards/captains/picard/ and resources/scans/base_game/boards/cb-picard-*.md."""

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
DECK = content().crew_deck("picard")
OWN = sorted(c.id for c in DECK if not c.same_as)  # the copies (Utilize, Recruit, ...) are tested with the originals


def me(s):
    return s.players[0]


def opp(s):
    return s.players[1]


def refresh(s):
    s.decision = None
    advance(s, flag_irreversible=False)


def picard(**kw):
    return given(deck="picard", opponent="soval", **kw)


def enterprise(s):
    return card(s, "1PIC02", zone="fleet")


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
    s = picard()
    p = me(s)
    assert p.captain.card == "1PIC01" and p.away_pool == 5 and [i.card for i in p.fleet] == ["1PIC02"]
    assert len(p.development) == 8 and len(p.reserve) == 4 and len(p.hand) + len(p.draw) == 10
    assert registry.OPS[("1PIC19", 0)].fn is registry.OPS[("2GEO18", 0)].fn  # Utilize
    assert registry.OPS[("1PIC02", 0)].fn is registry.OPS[("2GEO02", 0)].fn  # the Enterprise-D plays as the Shenzhou
    for c in DECK:
        for index, op in enumerate(c.operations):
            assert registry.has_code(c.id, index, op.kind), (c.id, c.name, index, op.kind)


NEEDS_OWN_SETUP = {
    ("1PIC03", 1),  # needs a secured neutral Location
    ("1PIC23", 1),  # needs an opponent Away Team beside yours
}


@pytest.mark.parametrize("cid,index", [(cid, i) for cid in OWN for i, op in enumerate(CARDS[cid].operations)
                                       if op.kind in ("PLAY", "ACTIVATION") and (cid, i) in registry.OPS])
def test_every_picard_operation_runs(cid, index):
    if (cid, index) in NEEDS_OWN_SETUP:
        pytest.skip("covered by its own test")
    kind = CARDS[cid].operations[index].kind
    tracks = {"research": 9, "influence": 9, "military": 9}
    if kind == "PLAY":
        position = {**RICH, "hand": RICH["hand"] + [cid], "tracks": tracks}
    else:
        z = zone_for(cid)
        position = {**RICH, z: [cid] if z == "duty" else RICH.get(z, []) + [cid], "tracks": tracks,
                    "hand": RICH["hand"] + ["1SHI11"]}  # a Starfleet Ship to free play
    for seed in range(2):
        s = picard(**position)
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
def test_random_games_with_picard(seed):
    rng = random.Random(seed)
    other = ["soval", "kirk", "sisko", "shran", "koloth", "sela"][seed]
    s = new_game(seed, "two_player", [SeatSetup("P", "picard", "advanced" if seed % 2 else "basic"),
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


def test_cadet_training_with_picard():
    s = new_game(2, "cadet", [SeatSetup("P", "picard", "advanced")], [], False, box="core")
    advance(s, flag_irreversible=False)
    rng = random.Random(2)
    for _ in range(4000):
        if s.step == "over":
            break
        ids = [o.id for o in s.decision.options]
        plays = [i for i in ids if i.startswith(("play:", "activate:", "mission:"))]
        choose(s, 0, rng.choice(plays) if plays and rng.random() < 0.85 else rng.choice(ids), flag_irreversible=False)
    assert s.step == "over"


# ------------------------------------------------------------------ the Captain

def test_picard_beams_a_gained_ally_and_scores_allies():
    s = picard(hand=["1PIC16", "2PER16"], empty_hand=True)
    glory = me(s).glory
    play(s, card(s, "1PIC16", zone="hand"), 1)  # Diplomacy: gain an Ally and log this card
    while s.decision.kind != "action":
        opts = options(s)
        answer(s, next((o for o in opts if o.startswith("Use") or "Enterprise" in o), opts[0]))
    allies = [b for b in enterprise(s).beamed if CARDS[b.card].suit == "Ally"]
    assert len(allies) == 1 and me(s).glory == glory + 1 and me(s).log[-1].card == "1PIC16"
    assert registry.ENDGAME["1PIC01"](s, me(s)) == 1 == score_player(s, me(s))["parts"]["endgame"]


# ------------------------------------------------------------------ Developments

def test_development_costs():
    assert all(c.id in registry.DEV_COSTS for c in DECK if c.position == "Development")
    broke = picard()
    me(broke).dilithium = me(broke).latinum = me(broke).glory = 0
    assert developments(broke) == []
    s = picard(dilithium=9, latinum=1, hand=["2PER16"], empty_hand=True)
    assert {"1PIC03", "1PIC04", "1PIC05", "1PIC06", "1PIC07", "1PIC10"} <= set(developments(s))
    from engine.ops import Actions

    start_dil, incidents = me(s).dilithium, len(s.incident)
    acts = Actions(Ctx(s, OpRef(mode="auto", seat=0)), ["ENLIST_DEVELOPMENT"])
    gen = acts.enlist_development(pred=lambda i: i.card == "1PIC04")
    try:
        ask = next(gen)
        while True:
            ask = gen.send(ask.options[0][0])
    except StopIteration:
        pass
    assert me(s).draw[0].card == "1PIC04" and me(s).dilithium == start_dil - 2 and len(s.incident) == incidents - 1


def test_make_it_so_takes_a_secured_location():
    s = picard(hand=["1PIC03"], tracks={"influence": 4})
    assert not can_play(s, card(s, "1PIC03", zone="hand"), 1)
    loc = s.neutral[0]
    loc.away[0] = 3
    refresh(s)
    play(s, card(s, "1PIC03", zone="hand"), 1)
    finish(s)
    assert any(i.uid == loc.uid for i in me(s).locations) and any(i.card == "1PIC03" for i in me(s).log)


def test_tamarians_pay_for_one_card_of_each_suit():
    s = picard(hand=["1PIC04"], empty_hand=True)
    me(s).draw[:0] = [s.new_inst("2PER16"), s.new_inst("2PER17"), s.new_inst("2CAR07")]
    glory = me(s).glory
    play(s, card(s, "1PIC04", zone="hand"), 0)
    answer(s, "Riva")
    assert "Rom" not in options(s)  # one Person only
    answer(s, "Holosuite")
    assert me(s).glory == glory + 2 and me(s).log[-1].card == "1PIC04" and [i.card for i in me(s).hand] == ["2PER17"]


def test_phasing_cloak_ignores_opponent_ships():
    from engine.ops import Actions

    s = picard(opp={"fleet": ["2SHI01"]})
    blocked = s.neutral[0]
    card(s, "2SHI01", seat=1, zone="fleet").at = blocked.uid
    acts = Actions(Ctx(s, OpRef(mode="auto", seat=0)), [])
    assert blocked not in acts.away_targets()
    s = picard(fleet=["1PIC05"], opp={"fleet": ["2SHI01"]})
    blocked = s.neutral[0]
    card(s, "2SHI01", seat=1, zone="fleet").at = blocked.uid
    assert blocked in Actions(Ctx(s, OpRef(mode="auto", seat=0)), []).away_targets()


def test_daystrom_institute_scores_synthetics():
    s = picard(locations=["1PIC06"], discard=["1PER17", "1PER05"])  # Peanut Hamper and B-4
    assert registry.ENDGAME["1PIC06"](s, me(s)) == 2
    hand = len(me(s).hand)
    activate(s, card(s, "1PIC06", zone="locations"), 3)
    assert len(me(s).hand) == hand + 1


def test_starbase_74_allows_a_second_duty_officer():
    s = picard(locations=["1PIC07"], duty=["2PER16"], hand=["2PER17"], empty_hand=True)
    activate(s, enterprise(s), 3)  # promote a Person from your hand
    finish(s)
    assert sorted(i.card for i in me(s).duty) == ["2PER16", "2PER17"]


def test_deanna_troi_gives_incidents_a_play():
    s = picard(duty=["1PIC08"], hand=["2INC06", "2PER16"], empty_hand=True)
    incident = card(s, "2INC06", zone="hand")
    assert can_play(s, incident, 101)
    play(s, incident, 101)
    finish(s)
    assert s.incident[-1].card == "2INC06" and len(me(s).hand) == 2
    without = picard(hand=["2INC06", "2PER16"], empty_hand=True)
    assert not can_play(without, card(without, "2INC06", zone="hand"), 101)


def test_geordi_free_plays_a_gained_ship():
    s = picard(duty=["1PIC09"], hand=["2GEO15"], empty_hand=True)  # Analyze: take an Incident to gain a Ship
    glory = me(s).glory
    play(s, card(s, "2GEO15", zone="hand"), 0)
    while s.decision.kind != "action":
        opts = options(s)
        answer(s, next((o for o in opts if o.startswith("Use") or o == "Yes"), opts[0]))
    assert me(s).glory == glory + 1


def test_bozeman_recalls_from_the_staging_area():
    s = picard(hand=["1PIC10"], staging=["2PER16"], tracks={"research": 6})
    play(s, card(s, "1PIC10", zone="hand"), 1)
    assert any(i.card == "2PER16" for i in me(s).hand)
    low = picard(hand=["1PIC10"], staging=["2PER16"], tracks={"research": 5})
    assert not can_play(low, card(low, "1PIC10", zone="hand"), 1)


# ------------------------------------------------------------------ the rest of the deck

def test_data_gains_a_track_for_every_five_logged_cards():
    s = picard(duty=["1PIC12"], hand=["2PER16"], empty_hand=True, log=["2PER17", "2PER22", "2CAR07", "2SHI01"])
    activate(s, card(s, "1PIC12", zone="duty"), 1)
    answer(s, "Military")
    assert me(s).tracks["military"] == 1 and len(me(s).log) == 5


def test_beverly_crusher_returns_a_taken_incident():
    s = picard(duty=["1PIC13"], hand=["2GEO15", "2PER16"], empty_hand=True)
    glory, incidents = me(s).glory, len(s.incident)
    play(s, card(s, "2GEO15", zone="hand"), 0)  # Analyze: take an Incident to gain a Ship
    while s.decision.kind != "action":
        opts = options(s)
        answer(s, next((o for o in opts if o.startswith("Use")), opts[0]))
    assert me(s).glory == glory + 1 and len(s.incident) == incidents
    assert not any(CARDS[i.card].suit == "Incident" for i in me(s).hand)


def test_type_7_shuttlecraft_sends_a_team_where_a_ship_is():
    s = picard(hand=["1PIC14"], empty_hand=True)
    target = s.neutral[1]
    enterprise(s).at = target.uid
    refresh(s)
    play(s, card(s, "1PIC14", zone="hand"), 0)
    answer(s, "Yes")
    target = next(loc for loc in s.neutral if loc.uid == target.uid)
    assert target.away.get(0) == 1 and me(s).draw[0].card == "1PIC14"


def test_farpoint_station_draws_for_away_teams():
    s = picard(locations=["1PIC21"], empty_hand=True)
    loc = card(s, "1PIC21", zone="locations")
    loc.away[0] = 3
    refresh(s)
    activate(s, card(s, "1PIC21", zone="locations"), 2)
    assert len(me(s).hand) == 2


def test_worf_removes_an_opponent_away_team():
    s = picard(duty=["1PIC23"], hand=["2PER16"], empty_hand=True)
    assert not can_activate(s, card(s, "1PIC23", zone="duty"), 1)
    loc = s.neutral[0]
    loc.away[0], loc.away[1] = 1, 2
    refresh(s)
    glory = me(s).glory
    activate(s, card(s, "1PIC23", zone="duty"), 1)
    finish(s)
    loc = next(i for i in s.neutral if i.uid == loc.uid)
    assert loc.away.get(1) == 1 and me(s).glory == glory + 1


def test_worf_play_discards_the_incident_and_sends_two_teams():
    s = picard(hand=["1PIC23"], empty_hand=True)
    play(s, card(s, "1PIC23", zone="hand"), 0)
    finish(s)
    assert max(loc.away.get(0, 0) for loc in s.neutral) == 2
    assert any(CARDS[i.card].suit == "Incident" for i in me(s).discard) and len(me(s).discard) >= 2


def test_will_riker_triggers_the_control_of_the_location_he_sends_to():
    s = picard(hand=["1PIC24"], empty_hand=True, locations=["1PIC21"], dilithium=1)
    research = me(s).tracks["research"]
    play(s, card(s, "1PIC24", zone="hand"), 0)
    while s.decision.kind != "action":
        opts = options(s)
        answer(s, next((o for o in opts if o == "Yes" or "Farpoint" in o), opts[0]))
    assert me(s).tracks["research"] == research + 1
    assert card(s, "1PIC21", zone="locations").away.get(0) == 1


def test_hand_size_is_five():
    assert hand_size(picard(), me(picard())) == 5


# ------------------------------------------------------------------ missions

def complete(s, mission_id):
    choose(s, 0, f"mission:{mission_id}", flag_irreversible=False)


def offered(s, mission_id):
    return f"mission:{mission_id}" in {o.id for o in s.decision.options}


def test_peace_negotiations():
    s = picard(tracks={"influence": 4, "research": 4})
    ship = enterprise(s)
    assert not offered(s, "peace-negotiations")
    ship.beamed.extend(s.new_inst(c) for c in ("2ALL02", "2ALL03", "2ALL04"))
    refresh(s)
    assert offered(s, "peace-negotiations")
    dilithium, hand = me(s).dilithium, len(me(s).hand)
    complete(s, "peace-negotiations")
    finish(s)
    assert me(s).dilithium == dilithium + 4 and len(me(s).hand) == hand + 4
    assert not enterprise(s).beamed and "peace-negotiations" in me(s).missions_completed  # the Allies are dismissed
    low = picard(tracks={"influence": 4})
    enterprise(low).beamed.extend(low.new_inst(c) for c in ("2ALL02", "2ALL03", "2ALL04"))
    refresh(low)
    assert not offered(low, "peace-negotiations")


def test_arbiter_of_succession_and_seek_out_new_life():
    s = picard(board="advanced")
    enterprise(s).beamed.extend(s.new_inst(c) for c in ("2PER10", "1PER04", "1PER07"))  # Lursa, Kamarag, Dorg
    refresh(s)
    actions, glory = me(s).actions, me(s).glory
    complete(s, "arbiter-of-succession")
    answer(s, "Military")
    finish(s)
    assert me(s).actions == actions + 1 and me(s).glory == glory + 1 and me(s).tracks["military"] == 1
    s = picard(board="advanced")
    # Klingon, Ferengi, Vulcan and Romulan (Talok has two), Kelpien, and one Alien card
    me(s).staging.extend(s.new_inst(c) for c in ("2PER10", "2PER17", "2PER21", "2ALL06", "2CAR08"))
    refresh(s)
    assert offered(s, "seek-out-new-life")
    encounters = len(s.encounter)
    complete(s, "seek-out-new-life")
    finish(s)
    assert len(s.encounter) == encounters - 1
    assert score_player(s, me(s))["parts"]["missions"] == 2
    few = picard(board="advanced")
    me(few).staging.extend(few.new_inst(c) for c in ("2PER10", "2PER17", "2ALL06", "2CAR08"))
    refresh(few)
    assert not offered(few, "seek-out-new-life")
