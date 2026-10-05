"""Common Incidents and Encounters (plans/card-implementation.md Step 9)."""

import pytest

from engine import cards as registry
from engine.content import content
from tests.scenario import activate, answer, can_play, card, given, options, play
from tests.test_market_cards import RICH, finish, table_zone

CARDS = content().cards
COMMON = sorted(k for k, c in CARDS.items() if c.is_common and c.suit in ("Incident", "Encounter")
                and not (c.position or "").startswith("Solo"))


def me(s):
    return s.players[0]


def opp(s):
    return s.players[1]


def uids(cards):
    return [i.uid for i in cards]


def implemented(kind):
    return [(cid, i) for cid in COMMON for i, op in enumerate(CARDS[cid].operations)
            if op.kind == kind and (cid, i) in registry.OPS]


NEEDS_OWN_SETUP = {
    ("2ENC05", 1),  # needs a beamed Incident
    ("2INC01", 1),  # needs a Kelpien in play
    ("0INC03", 0),  # needs a Directive in hand (the generous hand has Analyze, so this is offered)
}
COMMON_POSITION = {**RICH, "expansions": ["second_contact"], "promos": True,
                   "staging": ["2PER22", "2PER21", "2PER16", "2CAR13"], "locations": ["2GEO19"]}


@pytest.mark.parametrize("cid,index", implemented("PLAY") + implemented("ACTIVATION"))
def test_every_operation_runs(cid, index):
    op = CARDS[cid].operations[index]
    zone = "hand" if op.kind == "PLAY" else ("fleet" if "Ongoing" in CARDS[cid].traits else table_zone(cid))
    position = {**COMMON_POSITION, zone: COMMON_POSITION.get(zone, []) + [cid]}
    s = given(**position)
    inst = card(s, cid, zone=zone)
    legal = can_play(s, inst, index) if op.kind == "PLAY" else \
        f"activate:{inst.uid}:{index}" in {o.id for o in s.decision.options}
    if (cid, index) in NEEDS_OWN_SETUP and not legal:
        return
    assert legal, f"{cid} {index} {op.kind} is not available"
    for seed in range(2):
        trial = given(**position)
        (play if op.kind == "PLAY" else activate)(trial, card(trial, cid, zone=zone), index)
        finish(trial, seed)


def test_incidents_return_themselves():
    s = given(hand=["2INC03", "2PER16"])  # Riva: Influence icon
    incidents, lat = len(s.incident), me(s).latinum
    crisis = card(s, "2INC03", zone="hand")
    play(s, crisis, 0)
    answer(s, "Riva")
    assert s.incident[-1].uid == crisis.uid and len(s.incident) == incidents + 1 and me(s).latinum == lat + 1


def test_dilithium_shockwave_gives_the_opponent_dilithium():
    s = given(hand=["2INC01"], dilithium=3)
    theirs = opp(s).dilithium
    play(s, card(s, "2INC01", zone="hand"), 0)
    assert me(s).dilithium == 0 and opp(s).dilithium == theirs + 2


def test_subspace_rhapsody_puts_a_directive_and_refreshes_when_sung():
    s = given(hand=["0INC03", "2GEO15"], promos=True, empty_hand=True)  # Analyze is the only Directive
    me(s).captain.exhausted = True
    play(s, card(s, "0INC03", zone="hand"), 0)
    answer(s, "Yes")  # sang it
    assert not me(s).captain.exhausted and any(i.card == "2GEO15" for i in me(s).staging)


def test_stone_of_gol_exhaust_gives_glory_and_exhausted_officer_is_dismissed():
    s = given(hand=["2ENC07"], opp={"duty": ["2SOV05"]})
    glory = me(s).glory
    play(s, card(s, "2ENC07", zone="hand"), 0)
    assert s.decision.seat == 1
    answer(s, "Exhaust")
    assert opp(s).duty[0].exhausted and me(s).glory == glory + 1
    s = given(hand=["2ENC07"], opp={"duty": ["2SOV05"]})
    opp(s).duty[0].exhausted = True
    glory = me(s).glory
    play(s, card(s, "2ENC07", zone="hand"), 0)
    assert not opp(s).duty and me(s).glory == glory


def test_gomtuu_is_a_ship():
    s = given(hand=["2ENC02"], staging=["2PER13", "2PER18"])  # Research icon cards
    play(s, card(s, "2ENC02", zone="hand"), 0)
    answer(s, "Yes")
    gomtuu = card(s, "2ENC02", zone="fleet")
    from engine.cards.to_boldly_go._util import ships
    from engine.ops import Ctx
    from engine.state import OpRef

    assert gomtuu.uid in uids(ships(Ctx(s, OpRef(mode="auto", seat=0)))) and me(s).tracks["military"] >= 2


def test_guardian_of_forever_hand_size_and_junk_scans():
    from engine.game import hand_size

    s = given(fleet=["2ENC03"], expansions=["second_contact"])
    assert hand_size(s, me(s)) == 6
    from engine.ops import Actions, Ctx
    from engine.state import OpRef

    ctx = Ctx(s, OpRef(mode="auto", seat=0))
    assert Actions(ctx, [])._scans_junk()


def test_species_10c_counts_as_an_ally():
    s = given(staging=["2ENC06"])
    from engine.cards.to_boldly_go._util import is_suit

    assert is_suit(card(s, "2ENC06", zone="staging"), "Ally")


def test_delphic_sphere_is_wildcard_with_an_anomaly_deployed():
    from engine.ops import Ctx
    from engine.state import OpRef

    s = given(staging=["2ENC01"], fleet=["2CAR06"])  # Forced Singularity is an Anomaly
    assert "Wildcard" in Ctx(s, OpRef(mode="auto", seat=0)).traits(card(s, "2ENC01", zone="staging"))


def test_vger_logs_up_to_two():
    s = given(hand=["2ENC08"], discard=["2PER07", "2PER11"])
    play(s, card(s, "2ENC08", zone="hand"), 0)
    answer(s, "Hoshi")
    answer(s, "Malcolm")
    assert {"2PER07", "2PER11"} <= {i.card for i in me(s).log}
