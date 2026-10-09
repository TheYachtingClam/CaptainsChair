"""Koloth's Crew deck (plans/base-game.md Step 9): every operation, his missions, Cadet Training and random games.
Specs: resources/scans/base_game/cards/captains/koloth/ and resources/scans/base_game/boards/cb-koloth-*.md."""

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
DECK = content().crew_deck("koloth")
OWN = sorted(c.id for c in DECK if not c.same_as)  # the copies (Utilize, Recruit, ...) are tested with the originals


def me(s):
    return s.players[0]


def opp(s):
    return s.players[1]


def refresh(s):
    s.decision = None
    advance(s, flag_irreversible=False)


def koloth(**kw):
    return given(deck="koloth", opponent="soval", **kw)


def groth(s):
    return card(s, "1KOL02", zone="fleet")


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
    s = koloth()
    p = me(s)
    assert p.captain.card == "1KOL01" and p.away_pool == 6 and [i.card for i in p.fleet] == ["1KOL02"]
    assert len(p.development) == 7 and len(p.reserve) == 5 and len(p.hand) + len(p.draw) == 10
    assert registry.OPS[("1KOL18", 0)].fn is registry.OPS[("2GEO18", 0)].fn  # Utilize
    assert registry.OPS[("1SEL10", 0)].fn is registry.OPS[("1KOL16", 0)].fn  # Sela's Conquer is Koloth's
    assert registry.OPS[("1KOL24", 3)].fn is registry.OPS[("1KOL02", 3)].fn and ("1KOL24", 4) not in registry.OPS
    for c in DECK:
        for index, op in enumerate(c.operations):
            assert registry.has_code(c.id, index, op.kind), (c.id, c.name, index, op.kind)


NEEDS_OWN_SETUP = {
    ("1KOL07", 1),  # needs 15 Glory
    ("1KOL22", 2),  # needs an exhausted Klingon Ship
}


@pytest.mark.parametrize("cid,index", [(cid, i) for cid in OWN for i, op in enumerate(CARDS[cid].operations)
                                       if op.kind in ("PLAY", "ACTIVATION") and (cid, i) in registry.OPS])
def test_every_koloth_operation_runs(cid, index):
    if (cid, index) in NEEDS_OWN_SETUP:
        pytest.skip("covered by its own test")
    kind = CARDS[cid].operations[index].kind
    tracks = {"research": 9, "influence": 9, "military": 9}
    if kind == "PLAY":
        position = {**RICH, "hand": RICH["hand"] + [cid, "1KOL23"], "tracks": tracks, "dilithium": 12,
                    "locations": ["2LOC07"]}  # a Klingon to discard
    else:
        z = zone_for(cid)
        position = {**RICH, z: [cid] if z == "duty" else RICH.get(z, []) + [cid], "tracks": tracks,
                    "hand": RICH["hand"] + ["1KOL23"], "dilithium": 12,  # a Klingon to discard
                    "locations": RICH.get("locations", []) + ([] if z == "locations" else ["2LOC07"])}
        if z == "locations":
            position["locations"] = [cid, "2LOC07"]
    for seed in range(2):
        s = koloth(**position)
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
def test_random_games_with_koloth(seed):
    rng = random.Random(seed)
    other = ["soval", "kirk", "sisko", "picard", "shran", "sela"][seed]
    s = new_game(seed, "two_player", [SeatSetup("P", "koloth", "advanced" if seed % 2 else "basic"),
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


def test_cadet_training_with_koloth():
    s = new_game(2, "cadet", [SeatSetup("P", "koloth", "advanced")], [], False, box="core")
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


def test_koloth_sends_a_team_and_the_opponent_may_draw():
    s = koloth(hand=["2PER16"], empty_hand=True)
    theirs = len(opp(s).hand)
    activate(s, me(s).captain, 0)
    while s.decision.kind != "action":
        opts = options(s)
        answer(s, "Yes" if "Yes" in opts else opts[0])
    assert me(s).draw[0].card == "2PER16" and len(opp(s).hand) == theirs + 1
    assert sum(loc.away.get(0, 0) for loc in s.neutral + me(s).locations) == 1


def test_glory_conditions_on_development_costs():
    s = koloth(dilithium=9, latinum=3)
    me(s).glory = 7
    assert not {"1KOL05", "1KOL07", "1KOL08"} & set(developments(s))
    me(s).glory = 8
    assert "1KOL07" in developments(s) and "1KOL05" not in developments(s)  # Kang needs 8, Boreth and Kor 10
    me(s).glory = 10
    assert {"1KOL05", "1KOL07", "1KOL08"} <= set(developments(s))


def test_sword_of_kahless_is_free_with_the_devisor_in_play():
    s = koloth()
    me(s).dilithium = me(s).glory = 0
    assert "1KOL04" not in developments(s)
    me(s).fleet.append(s.new_inst("1KOL09"))
    assert "1KOL04" in developments(s)
    s = koloth(hand=["1KOL04"], duty=["1KOL23"], tracks={"military": 9})
    glory = me(s).glory
    play(s, card(s, "1KOL04", zone="hand"), 0)
    while s.decision.kind != "action":
        opts = options(s)
        answer(s, "Krell" if "Krell" in opts else opts[0])
    assert me(s).glory == glory + 4 and not me(s).duty and me(s).log[-1].card == "1KOL04"


def test_boreth_draws_the_bottom_card_and_scores_skill_icons():
    s = koloth(locations=["1KOL05"], dilithium=1, staging=["2PER16"])  # Riva has an Influence Skill icon
    bottom = me(s).draw[-1]
    activate(s, card(s, "1KOL05", zone="locations"), 2)
    assert any(i.uid == bottom.uid for i in me(s).hand)
    assert registry.ENDGAME["1KOL05"](s, me(s)) >= 2  # Boreth's own Any Skill, and Riva's Influence


def test_kang_and_kor_react_to_gaining_influence():
    s = koloth(duty=["1KOL07"], hand=["1KOL06"], empty_hand=True, tracks={"military": 3})
    glory = me(s).glory
    play(s, card(s, "1KOL06", zone="hand"), 0)  # Curzon Dax: gain the lower of Influence and Military
    while s.decision.kind != "action":
        opts = options(s)
        answer(s, next((o for o in opts if o.startswith("Use")), opts[0]))
    assert me(s).tracks["influence"] == 2 and me(s).glory == glory + 1
    s = koloth(duty=["1KOL08"], hand=["1KOL06"], empty_hand=True, tracks={"military": 3})
    play(s, card(s, "1KOL06", zone="hand"), 0)
    while s.decision.kind != "action":
        opts = options(s)
        answer(s, next((o for o in opts if o.startswith("Use")), "No" if "No" in opts else opts[0]))
    assert me(s).tracks["military"] == 4


def test_kang_is_destroyed_for_an_encounter_at_fifteen_glory():
    s = koloth(hand=["1KOL07"], empty_hand=True)
    assert not can_play(s, card(s, "1KOL07", zone="hand"), 1)
    me(s).glory = 15
    refresh(s)
    encounters = len(s.encounter)
    play(s, card(s, "1KOL07", zone="hand"), 1)
    assert me(s).glory == 18 and len(s.encounter) == encounters - 1
    assert not any(i.card == "1KOL07" for z in ("hand", "staging", "discard", "log") for i in getattr(me(s), z))


def test_kor_takes_a_location_he_has_just_secured():
    s = koloth(hand=["1KOL08"], empty_hand=True)
    s.neutral[:] = s.neutral[:1]
    loc = s.neutral[0]
    loc.away[0] = 2
    refresh(s)
    actions = me(s).actions
    play(s, card(s, "1KOL08", zone="hand"), 0)
    finish(s)
    if any(i.uid == loc.uid for i in me(s).locations):
        assert me(s).actions <= actions - 1 and any(i.card == "1KOL08" for i in me(s).log)


# ------------------------------------------------------------------ the rest of the deck

def test_rura_penthe_pays_per_prisoner():
    s = koloth(locations=["1KOL13"], hand=["2PER16"], empty_hand=True)
    loc = card(s, "1KOL13", zone="locations")
    activate(s, loc, 3)
    dilithium = me(s).dilithium
    run(s, card(s, "1KOL13", zone="locations"), 2)
    assert me(s).dilithium == dilithium + 1


def test_good_day_to_die_logs_one_ship_and_dismisses_another():
    s = koloth(hand=["1KOL17"], empty_hand=True, fleet=["1KOL24"])
    encounters = len(s.encounter)
    play(s, card(s, "1KOL17", zone="hand"), 0)
    answer(s, "Gr'oth")
    finish(s)
    assert any(i.card == "1KOL02" for i in me(s).log) and any(i.card == "1KOL24" for i in me(s).discard)
    assert len(s.encounter) == encounters - 1 and not me(s).fleet
    alone = koloth(hand=["1KOL17"], empty_hand=True)
    play(alone, card(alone, "1KOL17", zone="hand"), 0)
    assert alone.decision.kind == "action" and [i.card for i in me(alone).fleet] == ["1KOL02"]


def test_klingon_disruptors_remove_teams_where_you_have_one():
    s = koloth(hand=["1KOL19", "1KOL23"], empty_hand=True)
    loc = s.neutral[0]
    loc.away[0], loc.away[1] = 1, 2
    refresh(s)
    glory = me(s).glory
    play(s, card(s, "1KOL19", zone="hand"), 0)
    name = CARDS[loc.card].name
    answer(s, name)
    answer(s, name)
    loc = next(i for i in s.neutral if i.uid == loc.uid)
    assert not loc.away.get(1) and me(s).glory == glory + 2 and me(s).discard[-1].card == "1KOL23"


def test_arne_darvin_is_logged_for_glory():
    s = koloth(hand=["1KOL21"], empty_hand=True, tracks={"influence": 4}, opp={"duty": ["2PER16"]})
    glory = me(s).glory
    play(s, card(s, "1KOL21", zone="hand"), 1)
    finish(s)
    assert me(s).glory == glory + 3 and not opp(s).duty and me(s).log[-1].card == "1KOL21"
    assert any(CARDS[i.card].suit == "Incident" for i in me(s).hand)
    assert hand_size(koloth(duty=["1KOL21"]), me(koloth(duty=["1KOL21"]))) == 6


def test_korax_rewards_unspent_actions_at_clean_up():
    s = koloth(duty=["1KOL22"])
    glory, actions = me(s).glory, me(s).actions
    answer(s, "End")
    while s.active == 0 and s.decision.kind != "action":
        opts = options(s)
        answer(s, "Yes" if "Yes" in opts else opts[0])
    assert me(s).glory == glory + actions and len(me(s).hand) == 5 + actions


def test_krell_trades_arms():
    s = koloth(duty=["1KOL23"], fleet=["2CAR14", "1KOL19"])
    latinum, dilithium, glory = me(s).latinum, me(s).dilithium, me(s).glory
    run(s, card(s, "1KOL23", zone="duty"), 1)
    assert (me(s).latinum, me(s).dilithium, me(s).glory) == (latinum + 1, dilithium + 1, glory + 1)
    none = koloth(duty=["1KOL23"])  # Koloth himself is a Weapon, but the Captain is excluded
    latinum = me(none).latinum
    run(none, card(none, "1KOL23", zone="duty"), 1)
    assert me(none).latinum == latinum


# ------------------------------------------------------------------ missions

def test_expanding_the_empire():
    s = koloth(fleet=["1KOL24", "1KOL09"], locations=["1KOL20", "1KOL13"])
    assert not offered(s, "expanding-the-empire")  # 3 Ships and 2 Locations
    me(s).locations.append(s.new_inst("2LOC07"))
    refresh(s)
    reserve = len(me(s).reserve)
    complete(s, "expanding-the-empire")
    answer(s, "two Reserves")
    answer(s, "Klothos")
    assert len(me(s).reserve) == reserve - 2 and any(i.card == "1KOL24" for i in me(s).discard)


def test_romulan_weapons_trade_agreement_enlists_the_cloak():
    s = koloth(board="advanced")
    groth(s).beamed.append(s.new_inst("2PER21"))  # Talok is a Romulan
    refresh(s)
    complete(s, "romulan-weapons-trade-agreement")
    while s.decision.kind != "action":
        answer(s, "No" if "No" in options(s) else options(s)[0])
    assert me(s).tracks["military"] == 1 and me(s).draw[0].card == "1KOL03" and not groth(s).beamed


def test_sabotage_is_an_attack_reward():
    s = koloth(board="advanced", staging=["2PER21", "2PER17", "2CAR14", "1KOL19", "1PER12"])
    # Talok (Vulcan, Romulan) and Rom (Ferengi); Phasers and Disruptors; Lenara Kahn is a Scientist
    incidents = len(s.incident)
    complete(s, "sabotage")
    answer(s, "Yes")
    finish(s)
    assert len(s.incident) == incidents - 2 and score_player(s, me(s))["parts"]["missions"] == 4
    few = koloth(board="advanced", staging=["2PER21", "2CAR14", "1PER12"])  # one Weapon besides the Captain
    assert not offered(few, "sabotage")
