"""Soval's Crew deck (plans/card-implementation.md Step 11). Cases from each spec's Tests section."""

import pytest

from engine import cards as registry
from engine.content import content
from engine.game import advance, hand_size
from engine.ops import Ctx, duty_fits, Actions
from engine.scoring import score_player
from engine.state import OpRef
from tests.scenario import activate, answer, can_play, card, given, options, play
from tests.test_market_cards import RICH, finish

CARDS = content().cards
SOVAL = sorted(k for k in CARDS if k.startswith("2SOV"))


def me(s):
    return s.players[0]


def opp(s):
    return s.players[1]


def uids(cards):
    return [i.uid for i in cards]


def refresh(s):
    s.decision = None
    advance(s, flag_irreversible=False)


def soval(**kw):
    return given(deck="soval", opponent="georgiou", **kw)


def zone_for(cid):
    c = CARDS[cid]
    if c.suit == "Person":
        return "duty"
    if c.suit == "Location":
        return "locations"
    if c.suit == "Status":
        return "status"
    return "fleet"


@pytest.mark.parametrize("cid,index", [(cid, i) for cid in SOVAL for i, op in enumerate(CARDS[cid].operations)
                                       if op.kind in ("PLAY", "ACTIVATION") and (cid, i) in registry.OPS])
def test_every_soval_operation_runs(cid, index):
    kind = CARDS[cid].operations[index].kind
    if CARDS[cid].suit == "Captain":
        position = {**RICH, "staging": ["2SOV22"], "duty": ["2PER11"]}  # Malcolm Reed: a Human on duty
    elif kind == "PLAY":
        position = {**RICH, "hand": RICH["hand"] + [cid], "tracks": {"research": 9, "influence": 9, "military": 9}}
    else:
        z = zone_for(cid)
        position = {**RICH, z: [cid] if z in ("duty",) else RICH.get(z, []) + [cid]}
    for seed in range(2):
        s = soval(**position, log=["2SOV16"])
        inst = me(s).captain if CARDS[cid].suit == "Captain" else card(s, cid, zone="hand" if kind == "PLAY" else zone_for(cid))
        if kind == "PLAY":
            assert can_play(s, inst, index), f"{cid} {index} not playable"
            play(s, inst, index)
        else:
            if f"activate:{inst.uid}:{index}" not in {o.id for o in s.decision.options}:
                pytest.skip(f"{cid} {index} needs its own setup")
            activate(s, inst, index)
        finish(s, seed)


# --------------------------------------------------------------------------- spec Tests sections


def test_soval_dismisses_a_beamed_human_and_scores_non_vulcan_persons():
    s = soval(fleet=["2SOV10"])
    seleya = card(s, "2SOV10", zone="fleet")
    seleya.beamed.append(s.new_inst("2SOV22"))  # United Earth (Human), beamed
    refresh(s)
    hand = len(me(s).hand)
    activate(s, me(s).captain, 0)
    assert not seleya.beamed and len(me(s).hand) == hand + 2 and me(s).captain.exhausted
    s = soval()
    refresh(s)
    assert f"activate:{me(s).captain.uid}:0" not in {o.id for o in s.decision.options}


def test_soval_endgame_counts_owned_non_vulcan_persons():
    s = soval(empty_hand=True)
    me(s).draw.clear(), me(s).discard.clear()
    me(s).hand += [s.new_inst(c) for c in ("2PER11", "2PER07", "2PER14", "2SOV16", "2SOV21")]
    assert registry.ENDGAME["2SOV01"](s, me(s)) == 3


def test_vulcan_science_directorate_reaction_and_time_travel_passive():
    s = soval(hand=["2CAR13"])  # Orb of Time: Time Travel
    vsd = me(s).status[0]
    vsd.exhausted = True
    refresh(s)
    play(s, card(s, "2CAR13", zone="hand"), 0)
    while s.decision.kind == "op":
        answer(s, "No")
    assert vsd.uid in uids(me(s).log)


def test_vulcan_location_draws_and_gives_a_vulcan_slot():
    s = soval()
    vulcan = me(s).locations[0]
    vulcan.away[0] = 1
    refresh(s)
    hand = len(me(s).hand)
    activate(s, vulcan, 0)
    assert len(me(s).hand) == hand + 1
    assert duty_fits(s, me(s), [s.new_inst("2PER11"), s.new_inst("2SOV16")])  # one any + Muroc (Vulcan)
    assert not duty_fits(s, me(s), [s.new_inst("2PER11"), s.new_inst("2PER07")])


def test_mount_seleya_needs_a_vulcan_logged_to_enlist():
    s = soval()
    ctx = Ctx(s, OpRef(mode="auto", seat=0))
    from engine.ops import _payable_developments

    assert "2SOV04" not in [i.card for i in _payable_developments(ctx)]
    me(s).log.append(s.new_inst("2SOV16"))
    me(s).dilithium = 5
    assert "2SOV04" in [i.card for i in _payable_developments(ctx)]


def test_vulcan_hello_second_play_needs_military_9_and_skips_secured():
    s = soval(hand=["2SOV05"], tracks={"military": 8})
    assert not can_play(s, card(s, "2SOV05", zone="hand"), 1)
    s = soval(hand=["2SOV05"], tracks={"military": 9})
    secured = s.neutral[0]
    secured.away[1] = 3
    refresh(s)
    play(s, card(s, "2SOV05", zone="hand"), 1)
    names = " ".join(options(s)) if s.decision.kind == "op" else ""
    assert CARDS[secured.card].name not in names


def test_tpau_both_players_return_an_incident():
    s = soval(hand=["2SOV06", "2INC01"], opp={"hand": ["2INC03"]})
    glory = me(s).glory
    play(s, card(s, "2SOV06", zone="hand"), 0)
    answer(s, "Dilithium Shockwave")
    assert s.decision.seat == 1
    answer(s, "Political Crisis")
    while s.decision.kind == "op":
        answer(s, "No")
    assert me(s).glory == glory + 2


def test_kuvak_hand_size():
    s = soval(duty=["2SOV07"], locations=["2LOC02", "2LOC05"])
    assert hand_size(s, me(s)) == 7


def test_kirshara_needs_seven_vulcans():
    """Soval's starting Location, Vulcan, has the Vulcan trait: with 5 Murocs that is 6, with 6 it is 7."""
    s = soval(hand=["2SOV08"], staging=["2SOV16"] * 5)
    encounters = len(s.encounter)
    play(s, card(s, "2SOV08", zone="hand"), 0)
    assert len(s.encounter) == encounters and me(s).log[-1].card == "2SOV08"
    s = soval(hand=["2SOV08"], staging=["2SOV16"] * 6)
    encounters = len(s.encounter)
    play(s, card(s, "2SOV08", zone="hand"), 0)
    assert len(s.encounter) == encounters - 1 and me(s).log[-1].card == "2SOV08"


def test_paan_mokar_dismissed_at_clean_up_without_away_teams():
    s = soval(hand=["2SOV11"])
    play(s, card(s, "2SOV11", zone="hand"), 0)
    while s.decision.kind == "op":
        answer(s, "No")
    assert card(s, "2SOV11").uid in uids(me(s).locations)
    from tests.test_market_cards import choose_end

    choose_end(s)
    while s.decision.kind == "op":
        answer(s, "")
    assert card(s, "2SOV11").uid in uids(me(s).discard)


def test_vlar_reaction_after_an_ally():
    s = soval(duty=["2SOV12"], hand=["2ALL11"])
    glory, lat = me(s).glory, me(s).latinum
    play(s, card(s, "2ALL11", zone="hand"), 0)
    answer(s, "Use")
    assert me(s).glory == glory + 1 and me(s).latinum == lat + 1


def test_plomeek_tea_swaps_with_the_junk():
    s = soval(hand=["2SOV13"], expansions=["second_contact"], latinum=1)
    junk_ship = next((i for i in s.junk if CARDS[i.card].suit == "Ship"), None)
    assert junk_ship is not None
    market_ship = s.market["Ship"]
    play(s, card(s, "2SOV13", zone="hand"), 0)
    while s.decision.kind == "op":
        text = " ".join(options(s))
        answer(s, CARDS[junk_ship.card].name if CARDS[junk_ship.card].name in text else "No")
    assert s.market["Ship"].uid == junk_ship.uid and market_ship.uid in uids(s.junk)


def test_energy_drain_with_an_engineer_keeps_actions():
    s = soval(hand=["2SOV14"], staging=["2PER17"], dilithium=1)
    actions = me(s).actions
    play(s, card(s, "2SOV14", zone="hand"), 0)
    assert me(s).actions == actions and s.incident[-1].card == "2SOV14"


def test_stel_forces_dismissal_of_an_andorian():
    s = soval(hand=["2SOV15"], opp={"duty": ["2PER04"]})  # Commander Tysess: Andorian
    glory = me(s).glory
    play(s, card(s, "2SOV15", zone="hand"), 1)
    answer(s, "No")
    assert not opp(s).duty and me(s).glory == glory + 1


def test_muroc_all_three_logs_him():
    s = soval(hand=["2SOV16"], tracks={"influence": 6}, fleet=["2SOV24"])
    card(s, "2SOV24", zone="fleet").at = s.neutral[0].uid
    refresh(s)
    play(s, card(s, "2SOV16", zone="hand"), 0)
    answer(s, "Influence")
    answer(s, "Military")
    answer(s, "Send")
    assert me(s).log[-1].card == "2SOV16"


def test_idic_needs_all_three_for_an_encounter():
    s = soval(hand=["2SOV19"], staging=["2PER11"], fleet=["2SOV24"])
    me(s).locations[0].away[0] = 1
    refresh(s)
    play(s, card(s, "2SOV19", zone="hand"), 0)
    answer(s, "Vulcan")
    answer(s, "Malcolm")
    answer(s, "Ti'Mur")
    answer(s, "")
    assert CARDS[me(s).draw[0].card].suit == "Encounter"


def test_tpol_resupply_choice():
    s = soval(duty=["2SOV21"])
    tpol = card(s, "2SOV21", zone="duty")
    s.decision = None
    s.op_queue.append(OpRef(mode="auto", seat=0, uid=tpol.uid, index=1))
    advance(s, flag_irreversible=False)
    answer(s, "Spend 1 Dilithium")
    assert me(s).tracks["research"] == 1


def test_timur_second_play_needs_research_5():
    s = soval(hand=["2SOV24"], tracks={"research": 4})
    assert not can_play(s, card(s, "2SOV24", zone="hand"), 1)
