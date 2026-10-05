"""Rebner's Crew deck and missions (plans/card-implementation.md Step 17): hand size 3, Helmets, the Junk, and
Research and Influence fixed at x0."""

import pytest

from engine import cards as registry
from engine.content import content
from engine.game import advance, choose, hand_size
from engine.ops import A, Actions, Ctx, _payable_developments, start
from engine.state import OpRef
from tests.scenario import activate, answer, can_play, card, given, options, play
from tests.test_market_cards import RICH, finish

CARDS = content().cards
REBNER = sorted(k for k in CARDS if k.startswith("2REB"))


def me(s):
    return s.players[0]


def opp(s):
    return s.players[1]


def uids(cards):
    return [i.uid for i in cards]


def refresh(s):
    s.decision = None
    advance(s, flag_irreversible=False)


def rebner(**kw):
    return given(deck="rebner", opponent="soval", **kw)


def ctx(s):
    return Ctx(s, OpRef(mode="auto", seat=0))


def mondor(s):
    return next(i for i in me(s).fleet if i.card == "2REB02")


def zone_for(cid):
    suit = CARDS[cid].suit
    return {"Person": "duty", "Location": "locations", "Status": "status"}.get(suit, "fleet")


def resolve_all(s, prefer=("Yes",)):
    while s.decision is not None and s.decision.kind in ("op", "trigger"):
        opts = options(s)
        if s.decision.kind == "trigger":
            answer(s, next(o for o in opts if o.startswith("Do not")))
            continue
        answer(s, next((p for p in prefer for o in opts if p in o), ""))


def run_op(s, cid, index, zone):
    inst = card(s, cid, zone=zone)
    start(s, OpRef(mode="op", seat=0, uid=inst.uid, card=cid, index=index))


def wear(s, officer, helmet_id="2REB21"):
    officer.beamed.append(s.new_inst(helmet_id))


NEEDS_OWN_SETUP = {
    ("2REB01", 1),  # needs an empty hand: test_rebner_draws_with_an_empty_hand
    ("2REB08", 1),  # needs the Big Enough Helmet worn: test_pakled_emperor_wearing_the_big_enough_helmet
    ("2REB16", 1),  # Helmet costs: test_helmet_costs_on_ongoing_directives
    ("2REB16", 2),  # Military 15: test_pakled_decree_arsenal
    ("2REB18", 1),
    ("2REB20", 2),
    ("2REB20", 3),
}


@pytest.mark.parametrize("cid,index", [(cid, i) for cid in REBNER for i, op in enumerate(CARDS[cid].operations)
                                       if op.kind in ("PLAY", "ACTIVATION") and (cid, i) in registry.OPS])
def test_every_rebner_operation_runs(cid, index):
    if (cid, index) in NEEDS_OWN_SETUP:
        pytest.skip("covered by its own test")
    kind = CARDS[cid].operations[index].kind
    tracks = {"research": 9, "influence": 9, "military": 9}
    if CARDS[cid].suit == "Captain":
        position = {**RICH, "tracks": tracks}
    elif kind == "PLAY":
        position = {**RICH, "hand": RICH["hand"] + [cid, "2REB21"], "tracks": tracks}
    else:
        z = zone_for(cid)
        position = {**RICH, z: [cid] if z == "duty" else RICH.get(z, []) + [cid], "tracks": tracks,
                    "hand": RICH["hand"] + ["2REB21", "2PER07"]}
    for seed in range(2):
        s = rebner(**position)
        for ship in me(s).fleet:
            ship.at = s.neutral[0].uid
        refresh(s)
        if CARDS[cid].suit == "Captain":
            inst = me(s).captain
        else:
            inst = card(s, cid, zone="hand" if kind == "PLAY" else zone_for(cid))
        if kind == "PLAY":
            assert can_play(s, inst, index), f"{cid} {index} not playable"
            play(s, inst, index)
        else:
            assert f"activate:{inst.uid}:{index}" in {o.id for o in s.decision.options}, f"{cid} {index} not offered"
            activate(s, inst, index)
        finish(s, seed)


def test_shared_operations():
    for index in range(3):
        assert registry.OPS[("2REB11", index)].fn is registry.OPS[("2REB06", index)].fn
        assert registry.OPS[("2REB22", index)].fn is registry.OPS[("2REB21", index)].fn


# ------------------------------------------------------------------ deck rules (REQ-CD-REB)

def test_hand_size_is_three():
    s = rebner()
    assert hand_size(s, me(s)) == 3 and len(me(s).hand) == 3  # REQ-CD-REB-01


def test_research_and_influence_score_nothing():
    for side in ("basic", "advanced"):
        s = rebner(board=side)
        board = content().boards[me(s).board]
        for track in ("research", "influence"):
            assert all(board.multiplier(track, n) == 0 for n in range(16))  # REQ-CD-REB-02


def test_rebner_draws_with_an_empty_hand():
    s = rebner(empty_hand=True)
    refresh(s)
    assert f"activate:{me(s).captain.uid}:1" in {o.id for o in s.decision.options}
    activate(s, me(s).captain, 1)
    assert len(me(s).hand) == 2


def test_rebner_empty_hand_activation_needs_an_empty_hand():
    s = rebner()
    refresh(s)
    assert f"activate:{me(s).captain.uid}:1" not in {o.id for o in s.decision.options}


def test_rebner_endgame_counts_cargo_without_helmets():
    s = rebner(discard=["2CAR14", "2CAR05", "2CAR07", "2REB12"])
    owned_cargo = [i for i in me(s).hand + me(s).discard + me(s).draw + me(s).reserve + me(s).development
                   if CARDS[i.card].suit == "Cargo" and "Helmet" not in CARDS[i.card].traits]
    assert registry.ENDGAME["2REB01"](s, me(s)) == len(owned_cargo) // 2


def test_rumdar_reacts_to_rebners_draws():
    s = rebner(duty=["2REB09"], latinum=2)
    wear(s, card(s, "2REB09", zone="duty"))
    refresh(s)
    hand = len(me(s).hand)
    activate(s, me(s).captain, 2)  # spend 1 Latinum to draw 2
    assert s.decision.kind == "trigger" and "Rumdar" in " ".join(options(s))
    answer(s, "Rumdar")
    resolve_all(s, prefer=("No",))
    assert len(me(s).hand) == hand + 4


def test_rumdar_ignores_other_draws():
    s = rebner(duty=["2REB09"], hand=["2REB21"])
    play(s, card(s, "2REB21", zone="hand"), 1)  # Big Helmet: draw 2, discard 1
    resolve_all(s)
    assert s.decision.kind == "action"


# ------------------------------------------------------------------ Helmets (KW-HELM)

def test_pakled_planet_puts_a_helmet_on_a_duty_officer():
    s = rebner(locations=["2REB20"], duty=["2REB10"], hand=["2REB12"])
    refresh(s)
    planet = card(s, "2REB20", zone="locations")
    activate(s, planet, 3)
    resolve_all(s)
    grubdin = card(s, "2REB10", zone="duty")
    assert any(b.card in ("2REB21", "2REB22", "2REB12") for b in grubdin.beamed)
    # Only one Helmet per Duty Officer (KW-HELM-02): no bareheaded officer is left, so the Activation is not offered.
    planet = card(s, "2REB20", zone="locations")
    planet.exhausted = False
    refresh(s)
    assert f"activate:{planet.uid}:3" not in {o.id for o in s.decision.options}


def test_recalling_an_officer_brings_the_helmet_back():
    s = rebner(duty=["2REB10"], hand=["2REB14"])
    wear(s, card(s, "2REB10", zone="duty"))
    play(s, card(s, "2REB14", zone="hand"), 0)  # Red Alarm: recall a Duty Officer to return this card
    resolve_all(s, prefer=("Neither",))
    assert {"2REB10", "2REB21"} <= {i.card for i in me(s).hand}  # KW-HELM-03


def test_grubdin_wearing_a_helmet():
    s = rebner(duty=["2REB10"])
    wear(s, card(s, "2REB10", zone="duty"))
    refresh(s)
    military, latinum, glory = me(s).tracks["military"], me(s).latinum, me(s).glory
    activate(s, card(s, "2REB10", zone="duty"), 1)
    answer(s, "Yes")  # spend an Action for 1 Military per Helmet
    assert me(s).tracks["military"] == military + 1 and me(s).latinum == latinum + 1 and me(s).glory == glory + 1


def test_pakled_emperor_wearing_the_big_enough_helmet():
    s = rebner(duty=["2REB08"], dilithium=5)
    emperor = card(s, "2REB08", zone="duty")
    refresh(s)
    assert f"activate:{emperor.uid}:1" not in {o.id for o in s.decision.options}
    wear(s, emperor, "2REB03")
    refresh(s)
    activate(s, emperor, 1)
    resolve_all(s)
    assert {"2REB08", "2REB03"} <= {i.card for i in me(s).log}
    assert any(CARDS[i.card].suit == "Encounter" for i in me(s).hand)


def test_helmet_costs_on_ongoing_directives():
    s = rebner(fleet=["2REB16", "2REB18"], locations=["2REB20"], empty_hand=True)
    refresh(s)
    ids = {o.id for o in s.decision.options}
    for cid, index in (("2REB16", 1), ("2REB18", 1)):
        assert f"activate:{card(s, cid).uid}:{index}" not in ids  # REQ-CD-REB-04: needs a Helmet
    assert f"activate:{card(s, '2REB20').uid}:2" not in ids
    me(s).hand.append(s.new_inst("2REB21"))
    refresh(s)
    decree = card(s, "2REB16", zone="fleet")
    activate(s, decree, 1)
    resolve_all(s)
    assert any(b.card == "2REB21" for b in card(s, "2REB16", zone="fleet").beamed)


def test_pakled_decree_arsenal():
    s = rebner(fleet=["2REB16"], discard=["2CAR14"], tracks={"military": 15})
    refresh(s)
    decree = card(s, "2REB16", zone="fleet")
    activate(s, decree, 2)
    resolve_all(s)
    assert any(i.card == "2CAR14" for i in me(s).log)


def test_rebelution_dismisses_every_helmet_and_cannot_be_logged():
    s = rebner(duty=["2REB10"], fleet=["2REB16"], hand=["2REB15"], tracks={"military": 5})
    wear(s, card(s, "2REB10", zone="duty"))
    card(s, "2REB16", zone="fleet").beamed.append(s.new_inst("2REB22"))
    refresh(s)
    play(s, card(s, "2REB15", zone="hand"), 1)
    resolve_all(s)
    assert not card(s, "2REB10", zone="duty").beamed and not card(s, "2REB16", zone="fleet").beamed
    assert card(s, "2REB16", zone="fleet").exhausted
    assert s.neutral and any(loc.away.get(0) for loc in s.neutral + me(s).locations)  # 2 Helmets: an Away Team
    rebelution = card(s, "2REB15")
    acts = Actions(ctx(s), [A.LOG])
    list(acts.log(rebelution))
    assert rebelution not in me(s).log


def test_harpy_returns_to_the_top_of_the_deck():
    s = rebner(fleet=["2REB07"], hand=["2REB21"])
    refresh(s)
    activate(s, card(s, "2REB07", zone="fleet"), 2)
    resolve_all(s)
    assert me(s).draw[0].card == "2REB07"


# ------------------------------------------------------------------ Developments

def test_big_enough_helmet_cost_lets_the_opponent_draw():
    s = rebner(hand=["2ARC22"])
    hand = len(opp(s).hand)
    play(s, card(s, "2ARC22", zone="hand"), 1)
    answer(s, "Development")
    answer(s, "Big Enough Helmet")
    assert s.decision.seat == 1 and "Draw 2 cards" in s.decision.prompt
    answer(s, "Yes")
    resolve_all(s, prefer=("No",))
    assert len(opp(s).hand) == hand + 2 and me(s).draw[0].card == "2REB03"


def test_varuvian_bomb_free_with_a_team_on_karzill():
    s = rebner(dilithium=0, glory=0, locations=["2REB04"])
    me(s).dilithium = me(s).glory = 0
    assert "2REB05" not in {i.card for i in _payable_developments(ctx(s))}
    card(s, "2REB04", zone="locations").away[0] = 1
    assert "2REB05" in {i.card for i in _payable_developments(ctx(s))}


def test_karzill_clean_up_pays_for_unspent_actions():
    s = rebner(locations=["2REB04"])
    me(s).actions = 2
    dil, glory = me(s).dilithium, me(s).glory
    run_op(s, "2REB04", 2, "locations")
    resolve_all(s)
    assert me(s).dilithium == dil + 2 and me(s).glory == glory + 2
    assert registry.ENDGAME["2REB04"](s, me(s)) == me(s).glory // 4


def test_even_bigger_helmet_enlists_the_big_enough_helmet():
    s = rebner(hand=["2REB12"])
    play(s, card(s, "2REB12", zone="hand"), 1)
    resolve_all(s, prefer=("No",))
    assert me(s).draw[0].card == "2REB03"


def test_clumpship_forces_the_opponent_to_log_a_ship():
    s = rebner(hand=["2REB11"], opp={"fleet": ["2SHI01"]}, draw=["2CAR14"])
    play(s, card(s, "2REB11", zone="hand"), 0)
    seen = False
    while s.decision.kind in ("op", "trigger"):
        if s.decision.seat == 1 and "Log one of your Ships" in s.decision.prompt:
            seen = True
            answer(s, options(s)[0])
        elif s.decision.kind == "trigger":
            answer(s, next(o for o in options(s) if o.startswith("Do not")))
        else:
            opts = options(s)
            answer(s, next((o for o in opts if "Phaser" in o or CARDS["2CAR14"].name in o), opts[0]))
    assert seen and any(CARDS[i.card].suit == "Ship" for i in opp(s).log)


# ------------------------------------------------------------------ missions

def _offered(s, mission):
    return f"mission:{mission}" in {o.id for o in s.decision.options}


def test_things_that_make_us_smart_with_a_discount():
    s = rebner(staging=["2PER07", "3RIK13", "3PIK21"], latinum=1)  # Communication, Engineer, Scientist; no Pakled
    me(s).dilithium, me(s).latinum, me(s).glory = 0, 1, 0
    refresh(s)
    assert _offered(s, "things-that-make-us-smart")
    assert "2REB08" not in {i.card for i in _payable_developments(ctx(s))}  # The Pakled Emperor costs 2 Latinum
    choose(s, 0, "mission:things-that-make-us-smart", flag_irreversible=False)
    resolve_all(s, prefer=("Pakled Emperor", "Latinum"))
    assert me(s).draw[0].card == "2REB08" and me(s).latinum == 0 and me(s).glory == 2


def test_things_that_make_us_strong():
    s = rebner(board="advanced", staging=["2CAR14", "2CAR14"], tracks={"military": 6})
    refresh(s)
    assert _offered(s, "things-that-make-us-strong")
    choose(s, 0, "mission:things-that-make-us-strong", flag_irreversible=False)
    resolve_all(s)
    assert "things-that-make-us-strong" in me(s).missions_completed


def test_things_that_make_us_fast():
    s = rebner(board="advanced", fleet=["2SHI01", "2SHI02", "2SHI03"], dilithium=8)
    refresh(s)
    assert _offered(s, "things-that-make-us-fast")
    top = s.location_deck[0]
    choose(s, 0, "mission:things-that-make-us-fast", flag_irreversible=False)
    resolve_all(s, prefer=("No",))
    assert top.uid in uids(me(s).locations)


def test_samaritan_snare_beams_a_helmet_and_takes_an_incident():
    s = rebner(fleet=["2REB18"], hand=["2REB21"])
    refresh(s)
    activate(s, card(s, "2REB18", zone="fleet"), 1)
    resolve_all(s)
    assert any(b.card == "2REB21" for b in card(s, "2REB18", zone="fleet").beamed)
    assert any(CARDS[i.card].suit == "Incident" for i in me(s).hand)


def test_pakled_planet_muster_with_a_ship_there():
    s = rebner(locations=["2REB20"], hand=["2REB21"])
    planet = card(s, "2REB20", zone="locations")
    mondor(s).at = planet.uid
    refresh(s)
    glory = me(s).glory
    activate(s, planet, 2)
    resolve_all(s, prefer=("Pakled Planet",))
    assert card(s, "2REB20", zone="locations").away.get(0) and me(s).glory == glory + 1
