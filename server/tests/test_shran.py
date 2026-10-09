"""Shran's Crew deck (plans/base-game.md Step 8): every operation, his missions, Cadet Training and random games.
Specs: resources/scans/base_game/cards/captains/shran/ and resources/scans/base_game/boards/cb-shran-*.md."""

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
DECK = content().crew_deck("shran")
OWN = sorted(c.id for c in DECK if not c.same_as)  # the copies (Utilize, Recruit, ...) are tested with the originals


def me(s):
    return s.players[0]


def opp(s):
    return s.players[1]


def refresh(s):
    s.decision = None
    advance(s, flag_irreversible=False)


def shran(**kw):
    return given(deck="shran", opponent="soval", **kw)


def kumari(s):
    return card(s, "1SHR02", zone="fleet")


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
    s = shran()
    p = me(s)
    assert p.captain.card == "1SHR01" and p.away_pool == 5 and [i.card for i in p.fleet] == ["1SHR02"]
    assert len(p.development) == 7 and len(p.reserve) == 5 and len(p.hand) + len(p.draw) == 10
    assert registry.OPS[("1SHR22", 0)].fn is registry.OPS[("2GEO18", 0)].fn  # Utilize
    assert registry.OPS[("1KOL15", 0)].fn is registry.OPS[("1SHR17", 0)].fn  # Koloth's Confiscate is Shran's
    assert registry.OPS[("1SEL11", 1)].fn is registry.OPS[("1SHR16", 1)].fn  # Sela's Imperial Pride
    for c in DECK:
        for index, op in enumerate(c.operations):
            assert registry.has_code(c.id, index, op.kind), (c.id, c.name, index, op.kind)


NEEDS_OWN_SETUP = {
    ("1SHR16", 0),  # needs Away Teams on 3 controlled Locations
    ("1SHR07", 3),  # needs the Cruiser at a Location: the generic position puts every Ship at one
}
NEEDS_OWN_SETUP.discard(("1SHR07", 3))


@pytest.mark.parametrize("cid,index", [(cid, i) for cid in OWN for i, op in enumerate(CARDS[cid].operations)
                                       if op.kind in ("PLAY", "ACTIVATION") and (cid, i) in registry.OPS])
def test_every_shran_operation_runs(cid, index):
    if (cid, index) in NEEDS_OWN_SETUP:
        pytest.skip("covered by its own test")
    kind = CARDS[cid].operations[index].kind
    tracks = {"research": 9, "influence": 9, "military": 9}
    if kind == "PLAY":
        position = {**RICH, "hand": RICH["hand"] + [cid, "1SHR20"], "tracks": tracks, "dilithium": 12,
                    "locations": ["2LOC07"]}  # an Andorian to discard, a Location to log
    else:
        z = zone_for(cid)
        position = {**RICH, z: [cid] if z == "duty" else RICH.get(z, []) + [cid], "tracks": tracks,
                    "hand": RICH["hand"] + ["1SHR24", "1SHR19"], "dilithium": 12,  # Andorians to discard
                    "locations": RICH.get("locations", []) + ([] if z == "locations" else ["2LOC07"])}
        if z == "locations":
            position["locations"] = [cid, "2LOC07"]
    for seed in range(2):
        s = shran(**position)
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
def test_random_games_with_shran(seed):
    rng = random.Random(seed)
    other = ["soval", "kirk", "sisko", "picard", "koloth", "sela"][seed]
    s = new_game(seed, "two_player", [SeatSetup("P", "shran", "advanced" if seed % 2 else "basic"),
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


def test_cadet_training_with_shran():
    s = new_game(2, "cadet", [SeatSetup("P", "shran", "advanced")], [], False, box="core")
    advance(s, flag_irreversible=False)
    rng = random.Random(2)
    for _ in range(4000):
        if s.step == "over":
            break
        ids = [o.id for o in s.decision.options]
        plays = [i for i in ids if i.startswith(("play:", "activate:", "mission:"))]
        choose(s, 0, rng.choice(plays) if plays and rng.random() < 0.85 else rng.choice(ids), flag_irreversible=False)
    assert s.step == "over"


# ------------------------------------------------------------------ the Captain and his Developments

def complete(s, mission_id):
    choose(s, 0, f"mission:{mission_id}", flag_irreversible=False)


def offered(s, mission_id):
    return f"mission:{mission_id}" in {o.id for o in s.decision.options}


def test_shran_gains_dilithium_per_cargo_and_garrisons_a_location():
    s = shran(fleet=["2CAR14", "2CAR03"], hand=["2CAR07"], empty_hand=True, locations=["1SHR23"])
    dilithium = me(s).dilithium
    run(s, me(s).captain, 0)
    assert me(s).dilithium == dilithium + 2
    activate(s, me(s).captain, 1)
    assert card(s, "1SHR23", zone="locations").away.get(0) == 1 and me(s).discard[-1].card == "2CAR07"
    bare = shran(hand=["2CAR07"], empty_hand=True)
    assert not can_activate(bare, me(bare).captain, 1)  # no controlled Location


def test_aenar_costs_a_logged_weapon():
    s = shran()
    assert "1SHR03" in developments(s)  # Ushaan-Tor and Plasma Rifles are Weapons in his deck
    s = shran()
    for zone in (me(s).hand, me(s).draw, me(s).discard, me(s).reserve):
        zone[:] = [i for i in zone if "Weapon" not in CARDS[i.card].traits]
    assert "1SHR03" not in developments(s)


def test_tenebian_amethyst_pays_when_logged():
    s = shran(hand=["1SHR06", "2PER16"], empty_hand=True)
    glory, latinum = me(s).glory, me(s).latinum
    play(s, card(s, "1SHR06", zone="hand"), 0)
    answer(s, "Riva")
    finish(s)
    assert me(s).latinum == latinum + 2 and me(s).glory == glory + 3
    assert {i.card for i in me(s).log} == {"1SHR06", "2PER16"}


def test_coridan_scores_dilithium():
    s = shran(locations=["1SHR04"], dilithium=8, tracks={"influence": 7})
    assert registry.ENDGAME["1SHR04"](s, me(s)) == me(s).dilithium // 4 >= 2
    dilithium = me(s).dilithium
    run(s, card(s, "1SHR04", zone="locations"), 2)
    assert me(s).dilithium == dilithium + 2


def test_thoris_pays_for_every_incident_returned():
    s = shran(hand=["1SHR09", "2INC06"], empty_hand=True, opp={"hand": ["2INC03"]})
    glory = me(s).glory
    play(s, card(s, "1SHR09", zone="hand"), 0)
    answer(s, "Trade Embargo")
    assert s.decision.seat == 1
    answer(s, "Political Crisis")
    assert me(s).glory == glory + 2 and [i.card for i in s.incident[-2:]] == ["2INC06", "2INC03"]


# ------------------------------------------------------------------ the rest of the deck

def test_jhamel_finds_a_person_after_an_incident():
    s = shran(duty=["1SHR10"], hand=["2GEO15"], empty_hand=True, discard=["2PER16"])
    play(s, card(s, "2GEO15", zone="hand"), 0)  # Analyze: take an Incident to gain a Ship
    while s.decision.kind != "action":
        opts = options(s)
        answer(s, next((o for o in opts if o == "Yes" or "Riva" in o), opts[0]))
    assert "2PER16" in [i.card for i in me(s).hand]


def test_you_owe_me_one_reacts_to_either_players_utilize():
    s = shran(fleet=["1SHR11"], hand=["1SHR22"], empty_hand=True)
    theirs = opp(s).dilithium
    play(s, card(s, "1SHR22", zone="hand"), 0)
    while s.decision.kind != "action":
        opts = options(s)
        answer(s, next((o for o in opts if o.startswith("Use") or o.startswith("Draw a card;")), opts[0]))
    assert opp(s).dilithium == theirs + 2 and len(me(s).hand) == 1


def test_weytahn_is_dismissed_without_away_teams_and_scores_with_two():
    s = shran(locations=["1SHR12"], hand=["1SHR19"], empty_hand=True)
    loc = card(s, "1SHR12", zone="locations")
    activate(s, loc, 3)  # discard a Weapon: send an Away Team here, gain 1 Influence
    loc = card(s, "1SHR12", zone="locations")
    assert loc.away.get(0) == 1 and me(s).tracks["influence"] == 1 and registry.ENDGAME["1SHR12"](s, me(s)) == 0
    loc.away[0] = 2
    assert registry.ENDGAME["1SHR12"](s, me(s)) == 4
    loc.away.pop(0)
    refresh(s)
    answer(s, "End")
    finish(s)
    assert not any(i.card == "1SHR12" for i in me(s).locations) and any(i.card == "1SHR12" for i in me(s).discard)


def test_imperial_pride_costs():
    s = shran(hand=["1SHR16"], empty_hand=True, locations=["1SHR23", "1SHR12", "2LOC07"])
    assert not can_play(s, card(s, "1SHR16", zone="hand"), 0)
    for loc in me(s).locations:
        loc.away[0] = 1
    refresh(s)
    encounters = len(s.encounter)
    play(s, card(s, "1SHR16", zone="hand"), 0)
    finish(s)
    assert len(s.encounter) == encounters - 1 and all(not loc.away.get(0) for loc in me(s).locations)
    s = shran(hand=["1SHR16"], empty_hand=True, locations=["2LOC07"], dilithium=10)
    me(s).glory = 0
    dilithium = me(s).dilithium
    play(s, card(s, "1SHR16", zone="hand"), 1)
    finish(s)
    assert me(s).dilithium == dilithium - 10 and me(s).log[-1].card == "2LOC07"
    assert me(s).tracks["influence"] == 1  # Dozaria (Breen) shares no trait with Shran
    s = shran(hand=["1SHR16"], empty_hand=True, locations=["1SHR23"], dilithium=10)
    play(s, card(s, "1SHR16", zone="hand"), 1)
    finish(s)
    assert me(s).tracks["influence"] == 0  # Andoria is Andorian, as he is


def test_ushaan_tor_and_talas_dismiss():
    s = shran(hand=["1SHR19", "1SHR20"], empty_hand=True, opp={"duty": ["2PER16"]})
    play(s, card(s, "1SHR19", zone="hand"), 0)
    finish(s)
    assert not opp(s).duty
    s = shran(hand=["1SHR20"], empty_hand=True, opp={"duty": ["2PER21"]})  # Talok: Vulcan and Romulan
    play(s, card(s, "1SHR20", zone="hand"), 0)
    finish(s)
    assert not opp(s).duty and any(i.card == "2PER21" for i in opp(s).discard)


def test_tarah_discards_the_opponents_top_card():
    s = shran(hand=["1SHR21"], empty_hand=True)
    opp(s).draw.insert(0, s.new_inst("2PER16"))
    glory, incidents = me(s).glory, len(s.incident)
    play(s, card(s, "1SHR21", zone="hand"), 1)
    finish(s)
    assert me(s).glory == glory + 1 and opp(s).discard[-1].card == "2PER16" and len(s.incident) == incidents - 2
    s = shran(hand=["1SHR21"], empty_hand=True)
    opp(s).draw.insert(0, s.new_inst("2CAR07"))
    incidents = len(s.incident)
    play(s, card(s, "1SHR21", zone="hand"), 1)
    finish(s)
    assert len(s.incident) == incidents


def test_plasma_rifles_punish_a_controlled_location():
    s = shran(fleet=["1SHR24"], hand=["1SHR20"], empty_hand=True, opp={"locations": ["2LOC07"]})
    loc = card(s, "2LOC07", seat=1, zone="locations")
    loc.away[1] = 1
    refresh(s)
    incidents = len(s.incident)
    activate(s, card(s, "1SHR24", zone="fleet"), 1)
    finish(s)
    assert not card(s, "2LOC07", seat=1, zone="locations").away.get(1) and len(s.incident) == incidents - 1
    assert any(i.card == "1SHR24" for i in me(s).discard)


# ------------------------------------------------------------------ missions

def test_securing_andorias_borders():
    s = shran(locations=["1SHR23", "1SHR12", "2LOC07"], staging=["1SHR19", "1SHR24", "2CAR14"])
    assert not offered(s, "securing-andorias-borders")  # three Weapons
    me(s).staging.append(s.new_inst("1CAR09"))
    refresh(s)
    actions = me(s).actions
    complete(s, "securing-andorias-borders")
    finish(s)
    assert me(s).actions == actions + 1 and "securing-andorias-borders" in me(s).missions_completed


def test_founding_the_federation_needs_four_different_cards():
    s = shran(board="advanced")
    # Harry Mudd (Human), Talok (Vulcan), Riva (Ambassador, Communication), Tevrin Krit (Tellarite)
    kumari(s).beamed.extend(s.new_inst(c) for c in ("2PER06", "2PER21", "2PER16", "2PER22"))
    refresh(s)
    assert offered(s, "founding-the-federation")
    complete(s, "founding-the-federation")
    finish(s)
    assert all(me(s).tracks[t] == 2 for t in ("research", "influence", "military"))
    # The Kumari is itself an Andorian on the Ship (REQ-MS-03), so three beamed cards were enough and Riva stays.
    assert [b.card for b in kumari(s).beamed] == ["2PER16"]
    few = shran(board="advanced")
    kumari(few).beamed.extend(few.new_inst(c) for c in ("2PER06", "2PER21"))  # Human, Vulcan, and the Andorian Ship
    refresh(few)
    assert not offered(few, "founding-the-federation")


def test_andorian_mining_consortium():
    s = shran(board="advanced", staging=["2PER22", "2CAR07", "1SHR06"])  # three Business
    latinum, glory = me(s).latinum, me(s).glory
    complete(s, "andorian-mining-consortium")
    while s.decision.kind != "action":
        opts = options(s)
        answer(s, "No" if "No" in opts else opts[0])
    assert me(s).latinum == latinum + 2 and me(s).glory == glory + 1
    assert score_player(s, me(s))["parts"]["missions"] == 3
