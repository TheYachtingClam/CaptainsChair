"""Locations, the Reward pile and Stardates (plans/card-implementation.md Step 10)."""

import pytest

from engine import cards as registry
from engine.content import content
from engine.game import advance
from engine.scoring import score_player
from engine.state import OpRef
from tests.scenario import activate, answer, can_play, card, given, options, play
from tests.test_market_cards import RICH, _matching_event, finish

CARDS = content().cards
LOCATIONS = sorted(k for k, c in CARDS.items() if c.is_common and c.suit == "Location")
REWARDS = sorted(k for k, c in CARDS.items() if c.position == "Rewards")
POSITION = {**RICH, "expansions": ["second_contact"], "promos": True,
            "staging": ["2PER22", "2PER21", "2PER16", "2CAR13"]}


def me(s):
    return s.players[0]


def opp(s):
    return s.players[1]


def uids(cards):
    return [i.uid for i in cards]


def refresh(s):
    s.decision = None
    advance(s, flag_irreversible=False)


def ops_of(ids, kinds):
    return [(cid, i) for cid in ids for i, op in enumerate(CARDS[cid].operations)
            if op.kind in kinds and (cid, i) in registry.OPS]


# --------------------------------------------------------------------------- exercisers


@pytest.mark.parametrize("cid,index", ops_of(LOCATIONS, ("CONTROL", "RESUPPLY", "CLEAN-UP", "ACTIVATION", "REACTION",
                                                          "SPECIAL")))
def test_every_location_operation_runs(cid, index):
    kind = CARDS[cid].operations[index].kind
    for seed in range(2):
        s = given(**{**POSITION, "locations": [cid]})
        loc = card(s, cid, zone="locations")
        loc.away[0] = 2
        loc.beamed.append(s.new_inst("2PER07"))
        me(s).fleet[0].at = loc.uid  # a Ship of yours here (Tulgana IV)
        refresh(s)
        if kind == "ACTIVATION":
            assert f"activate:{loc.uid}:{index}" in {o.id for o in s.decision.options}
            activate(s, loc, index)
        else:
            ev = _matching_event(s, cid, index) if registry.OPS[(cid, index)].trigger else None
            if kind in ("REACTION", "SPECIAL") and ev is None:
                ev = {"kind": "log", "seat": 0, "uid": loc.uid, "by": 0}  # Tahal-Meeroj's own log trigger
            s.decision = None
            s.op_queue.append(OpRef(mode="trigger" if ev else "auto", seat=0, uid=loc.uid, index=index, event=ev))
            advance(s, flag_irreversible=False)
        finish(s, seed)


@pytest.mark.parametrize("cid,index", ops_of(REWARDS, ("PLAY", "ACTIVATION")))
def test_every_reward_operation_runs(cid, index):
    kind = CARDS[cid].operations[index].kind
    zone = "hand" if kind == "PLAY" else "duty"
    position = {**POSITION, zone: [cid] if zone == "duty" else POSITION["hand"] + [cid]}
    for seed in range(2):
        s = given(**position)
        inst = card(s, cid, zone=zone)
        if kind == "PLAY":
            assert can_play(s, inst, index)
            play(s, inst, index)
        else:
            activate(s, inst, index)
        finish(s, seed)


# --------------------------------------------------------------------------- Locations


def test_krulmuth_b_takes_a_reward_and_destroys_the_other():
    s = given(locations=["3LOC01"], expansions=["second_contact"])
    krul = card(s, "3LOC01", zone="locations")
    krul.away[0] = 1
    rewards = len(s.rewards)
    refresh(s)
    activate(s, krul, 1)
    answer(s, "")
    assert len(s.rewards) == rewards - 2
    assert any(CARDS[i.card].position == "Rewards" for i in me(s).hand)


def test_starbase_80_takes_incidents_from_the_junk_and_gains_from_it():
    s = given(locations=["0LOC01"], hand=["2GEO15"], promos=True)
    s.junk.append(s.new_inst("2INC05"))
    incidents = len(s.incident)
    play(s, card(s, "2GEO15", zone="hand"), 0)  # Analyze: take an Incident (cost) to gain a Ship
    answer(s, "Subspace Phenomenon")
    assert len(s.incident) == incidents and any(i.card == "2INC05" for i in me(s).hand)


def test_solum_puts_the_incident_on_the_bottom_of_the_deck():
    s = given(locations=["2LOC16"])
    from engine.ops import Ctx, Actions

    loc = card(s, "2LOC16", zone="locations")
    s.decision = None
    s.op_queue.append(OpRef(mode="auto", seat=0, uid=loc.uid, index=0))
    advance(s, flag_irreversible=False)
    assert CARDS[me(s).draw[-1].card].suit == "Incident"
    _ = Ctx, Actions


def test_tahal_meeroj_gives_research_when_logged():
    s = given(hand=["2GEO17"], locations=["2LOC10"])  # Strange New Worlds logs a controlled Location
    play(s, card(s, "2GEO17", zone="hand"), 0)
    while s.decision.kind == "op":
        answer(s, "Tahal" if "Tahal" in " ".join(options(s)) else "")
    assert me(s).tracks["research"] == 1 + 2


def test_xahea_duplicates_utilizes_other_operation():
    s = given(hand=["2GEO18", "2PER07"], locations=["2LOC20"])
    dil = me(s).dilithium
    play(s, card(s, "2GEO18", zone="hand"), 1)  # Utilize: gain on a Specialty track per icon
    answer(s, "Research")
    assert s.decision.kind == "trigger" and "Xahea" in options(s)[0]
    answer(s, "Xahea")
    while s.decision.kind == "op":
        answer(s, "")  # duplicate Utilize's Dilithium operation
    assert me(s).dilithium > dil  # Utilize's Dilithium operation resolved too


def test_khitomer_gives_an_incident_for_an_opponent_attack():
    s = given(locations=["2LOC14"], opp={"hand": ["2PER12", "2CAR14"]})
    from tests.test_market_cards import choose_end, run_to_action_for

    choose_end(s)
    run_to_action_for(s, 1)
    hand = len(opp(s).hand)
    play(s, card(s, "2PER12", seat=1, zone="hand"), 0)  # Malik (Attack), discarding Phasers
    while s.decision.kind in ("op",):
        answer(s, "")
    if s.decision.kind == "trigger" and s.decision.seat == 0:
        answer(s, "Khitomer")
    assert len(opp(s).hand) == hand - 2 + 1


def test_cold_station_12_beams_a_card_discarded_in_the_action_step():
    s = given(locations=["2LOC04"], hand=["2INC03", "2PER16"])
    play(s, card(s, "2INC03", zone="hand"), 0)  # Political Crisis: discard a card
    answer(s, "Riva")
    assert s.decision.kind == "trigger"
    answer(s, "Cold Station")
    assert [b.card for b in card(s, "2LOC04", zone="locations").beamed] == ["2PER16"]


# --------------------------------------------------------------------------- Rewards


def test_reward_cards_score_minus_unless_logged():
    s = given(staging=["3PER01"], log=["3PER04"], expansions=["second_contact"])
    parts = score_player(s, me(s))["parts"]["printed_vp"]
    s2 = given(expansions=["second_contact"])
    base = score_player(s2, s2.players[0])["parts"]["printed_vp"]
    assert parts == base - 2  # Spock in play: -2; Chef Riker logged: 0


def test_ensigns_cannot_be_promoted():
    s = given(hand=["3ALL02", "3PER05"], expansions=["second_contact"])
    play(s, card(s, "3ALL02", zone="hand"), 0)  # Illyrians: promote a Person from hand or Staging Area
    while s.decision.kind == "op":
        answer(s, "Boimler" if "Boimler" in " ".join(options(s)) else "")
    assert not any(i.card == "3PER05" for i in me(s).duty)


def test_spock_slot_takes_a_vulcan_romulan_or_ambassador():
    from engine.ops import duty_fits

    s = given(duty=["3PER01"], expansions=["second_contact"])
    assert duty_fits(s, me(s), [*me(s).duty, s.new_inst("2PER16")])  # Riva: Ambassador
    assert not duty_fits(s, me(s), [*me(s).duty, s.new_inst("2PER10")])  # Lursa: Klingon


def test_dax_scans_instead_of_gaining():
    s = given(duty=["3PER07"], hand=["2GEO15"], expansions=["second_contact"])
    hand = len(me(s).hand)
    play(s, card(s, "2GEO15", zone="hand"), 0)  # Analyze: take an Incident to gain a Ship
    assert s.decision.kind == "op" and "Dax" in " ".join(options(s))
    answer(s, "Lieutenant Dax")
    answer(s, "")  # pick from the 2 scanned Ships
    answer(s, "Discard pile")
    assert len(me(s).hand) == hand - 1 + 1 + 1  # Incident taken, and Dax's draw


def test_gowron_after_taking_control():
    s = given(duty=["3PER03"], tracks={"military": 5}, expansions=["second_contact"])
    loc = s.neutral[0]
    loc.away[0] = 3
    from engine.game import choose

    hand = len(me(s).hand)
    me(s).controls_this_turn = 0
    s.step, s.decision = "control", None
    advance(s, flag_irreversible=False)
    choose(s, 0, f"take:{loc.uid}", flag_irreversible=False)
    while s.decision.kind == "op":
        answer(s, "")
    assert s.decision.kind == "trigger" and "Gowron" in options(s)[0]
    hand = len(me(s).hand)  # the Location's own CONTROL may have changed it
    answer(s, "Gowron")
    answer(s, "Draw")
    answer(s, "Junk")
    answer(s, "")
    assert len(me(s).hand) == hand + 1


# --------------------------------------------------------------------------- Stardates


KNOWN_STARDATE_EFFECTS = {
    "WHEN EMPTIED": ("Destroy this card.", "Put this card in the inactive player's Staging Area.",
                     "Put this card in your Staging Area.", "Trigger the end of the game."),
    "STARDATE RESOLUTION": ("Wipe the Market (removing all tokens).",
                            "Wipe the Market (removing all tokens) and any neutral Location with no tokens present."),
}


def test_every_stardate_effect_is_one_the_engine_knows():
    """The engine resolves Stardates by their printed effect (engine/game.py empty_stardate, step_cleanup). A new
    Stardate with an unknown effect must fail here rather than be silently ignored."""
    for cid, c in CARDS.items():
        if c.suit != "Stardate":
            continue
        for op in c.operations:
            known = KNOWN_STARDATE_EFFECTS[op.kind]
            assert any((op.text or "").startswith(k) for k in known), f"{cid}: unknown {op.kind}: {op.text}"
