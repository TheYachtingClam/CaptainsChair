"""Kirk's Crew deck and missions (plans/card-implementation.md Step 12)."""

import pytest

from engine import cards as registry
from engine.content import content
from engine.game import advance
from engine.ops import Ctx, _payable_developments
from engine.state import OpRef
from tests.scenario import activate, answer, can_play, card, given, options, play
from tests.test_market_cards import RICH, finish

CARDS = content().cards
KIRK = sorted(k for k in CARDS if k.startswith("2KIRK"))


def me(s):
    return s.players[0]


def opp(s):
    return s.players[1]


def uids(cards):
    return [i.uid for i in cards]


def refresh(s):
    s.decision = None
    advance(s, flag_irreversible=False)


def kirk(**kw):
    return given(deck="kirk", opponent="soval", **kw)


def zone_for(cid):
    suit = CARDS[cid].suit
    return {"Person": "duty", "Location": "locations", "Status": "status"}.get(suit, "fleet")


NEEDS_OWN_SETUP = {
    ("2KIRK16", 1),  # needs a Time Travel card in play (same as Subspace Phenomenon 2INC05, tested in Step 9)
    ("2KIRK17", 1),  # needs a Person beamed to the Levitation Boots: test_levitation_boots_recall
}


@pytest.mark.parametrize("cid,index", [(cid, i) for cid in KIRK for i, op in enumerate(CARDS[cid].operations)
                                       if op.kind in ("PLAY", "ACTIVATION") and (cid, i) in registry.OPS])
def test_every_kirk_operation_runs(cid, index):
    if (cid, index) in NEEDS_OWN_SETUP:
        pytest.skip("covered by its own test")
    kind = CARDS[cid].operations[index].kind
    tracks = {"research": 9, "influence": 9, "military": 9}
    if CARDS[cid].suit == "Captain":
        position = {**RICH, "discard": RICH["discard"] + ["2KIRK20"], "tracks": tracks}
    elif kind == "PLAY":
        position = {**RICH, "hand": RICH["hand"] + [cid], "tracks": tracks}
    else:
        z = zone_for(cid)
        position = {**RICH, z: [cid] if z == "duty" else RICH.get(z, []) + [cid], "tracks": tracks}
    for seed in range(2):
        s = kirk(**position)
        for ship in me(s).fleet:
            ship.at = s.neutral[0].uid  # Ships at a Location, for "log a deployed Ship at a Location"
        refresh(s)
        inst = me(s).captain if CARDS[cid].suit == "Captain" else card(s, cid, zone="hand" if kind == "PLAY" else zone_for(cid))
        if kind == "PLAY":
            assert can_play(s, inst, index), f"{cid} {index} not playable"
            play(s, inst, index)
        else:
            assert f"activate:{inst.uid}:{index}" in {o.id for o in s.decision.options}, f"{cid} {index} not offered"
            activate(s, inst, index)
        finish(s, seed)


def test_enterprise_refit_shares_the_shenzhou_operations():
    for index in range(4):
        assert registry.OPS[("2KIRK02", index)].fn is registry.OPS[("2GEO02", index)].fn


def test_kirk_endgame_lowest_track():
    s = kirk(tracks={"research": 7, "influence": 5, "military": 9})
    assert registry.ENDGAME["2KIRK01"](s, me(s)) == 2


def test_kirk_reaction_after_a_klingon():
    s = kirk(hand=["2PER10"])  # Lursa: Klingon
    play(s, card(s, "2PER10", zone="hand"), 0)
    while s.decision.kind == "op":
        answer(s, "No")
    assert s.decision.kind == "trigger" and "James T. Kirk" in options(s)[0]
    answer(s, "James")
    answer(s, "")
    assert me(s).tracks["military"] == 1


def test_enterprise_a_free_when_refit_logged():
    s = kirk(dilithium=0)
    ctx = Ctx(s, OpRef(mode="auto", seat=0))
    assert "2KIRK05" not in [i.card for i in _payable_developments(ctx)]
    refit = me(s).fleet[0]
    me(s).fleet.remove(refit)
    me(s).log.append(refit)
    assert "2KIRK05" in [i.card for i in _payable_developments(ctx)]


def test_excelsior_free_with_sulu_on_duty():
    s = kirk(duty=["2KIRK07"], dilithium=0)
    assert "2KIRK06" in [i.card for i in _payable_developments(Ctx(s, OpRef(mode="auto", seat=0)))]


def test_sulu_ignores_an_attack_by_exhausting_a_ship():
    s = kirk(opp={"hand": ["2PER12", "2CAR14"]}, duty=["2KIRK07"])
    from tests.test_market_cards import choose_end, run_to_action_for

    choose_end(s)
    run_to_action_for(s, 1)
    glory = me(s).glory
    play(s, card(s, "2PER12", seat=1, zone="hand"), 0)  # Malik steals 1 Glory
    assert s.decision.seat == 0 and "Hikaru Sulu" in " ".join(options(s))
    answer(s, "Hikaru Sulu")
    assert me(s).glory == glory and me(s).fleet[0].exhausted


def test_levitation_boots_dismissed_when_empty():
    s = kirk(hand=["2KIRK17"], empty_hand=True)
    play(s, card(s, "2KIRK17", zone="hand"), 0)
    answer(s, "Stop")  # beam nobody
    assert card(s, "2KIRK17").uid in uids(me(s).discard)


def test_levitation_boots_recall():
    s = kirk(fleet=["2KIRK17"])
    boots = card(s, "2KIRK17", zone="fleet")
    boots.beamed += [s.new_inst("2PER07"), s.new_inst("2PER11")]
    refresh(s)
    activate(s, boots, 1)
    answer(s, "Hoshi")
    assert any(i.card == "2PER07" for i in me(s).hand)
    assert [b.card for b in card(s, "2KIRK17", zone="fleet").beamed] == ["2PER11"]  # objects are rebuilt on resume


def test_starfleet_hq_sends_away_teams_when_logged():
    """Strange New Worlds logs Starfleet Headquarters; its SPECIAL sends up to X Away Teams, X being the current
    Stardate's sequence number (1 at the start)."""
    from tests.scenario import name as card_name

    s = kirk(hand=["2KIRK21"])
    hq = me(s).locations[0]
    play(s, card(s, "2KIRK21", zone="hand"), 0)
    while s.decision.kind == "op":
        answer(s, "Yes" if "Yes" in options(s) else "")
    assert hq.uid in uids(me(s).log)
    teams = sum(loc.away.get(0, 0) for loc in s.neutral)
    assert teams == 1 and CARDS[s.stardates[0].card].sequence == 1
    _ = card_name


def test_where_no_man_has_gone_before():
    s = kirk(tracks={"research": 4})
    refit = me(s).fleet[0]
    refit.beamed += [s.new_inst("2ENC08"), s.new_inst("2ENC04")]
    refresh(s)
    glory = s.stardate_glory
    from engine.game import choose

    choose(s, 0, "mission:where-no-man-has-gone-before", flag_irreversible=False)
    assert any(CARDS[i.card].suit == "Encounter" for i in me(s).hand) and s.stardate_glory == glory - 2
    assert not refit.beamed  # the beamed Encounters that met the goal are dismissed


def test_search_for_spock():
    s = kirk(board="advanced", log=["2KIRK24"], fleet=["2KIRK11"],
             staging=["2PER11", "2PER07", "2PER14", "2KIRK12", "2KIRK13"], tracks={"military": 4})
    refresh(s)
    assert any("Search for Spock" in o.label for o in s.decision.options)
    from engine.game import choose

    choose(s, 0, "mission:search-for-spock", flag_irreversible=False)
    while s.decision.kind == "op":
        answer(s, "No" if "No" in options(s) else "")
    assert any(i.card == "2KIRK24" for i in me(s).hand) and card(s, "2KIRK11").uid in uids(me(s).discard)


def test_cadet_ignores_stardate_glory_removal_outside_clean_up():
    s = given(deck="kirk", mode="cadet", tracks={"research": 4})
    me(s).fleet[0].beamed += [s.new_inst("2ENC08"), s.new_inst("2ENC04")]
    refresh(s)
    glory = s.stardate_glory
    from engine.game import choose

    choose(s, 0, "mission:where-no-man-has-gone-before", flag_irreversible=False)
    assert s.stardate_glory == glory  # REQ-CTM-11
