"""Riker's Crew deck and missions (plans/card-implementation.md Step 15)."""

import pytest

from engine import cards as registry
from engine.content import content
from engine.game import advance, choose
from engine.ops import Ctx, _payable_developments, start, traits_of
from engine.state import OpRef
from engine.views import game_view
from tests.scenario import activate, answer, can_play, card, given, options, play
from tests.test_market_cards import RICH, finish

CARDS = content().cards
SHARED = {"3RIK08", "3RIK17", "3RIK18", "3RIK19", "3RIK20"}  # PLAYs shared with other decks, tested there
RIKER = sorted(k for k in CARDS if k.startswith("3RIK") and k not in SHARED)


def me(s):
    return s.players[0]


def opp(s):
    return s.players[1]


def uids(cards):
    return [i.uid for i in cards]


def refresh(s):
    s.decision = None
    advance(s, flag_irreversible=False)


def riker(**kw):
    kw.setdefault("expansions", ["second_contact"])
    return given(deck="riker", opponent="soval", **kw)


def ctx(s):
    return Ctx(s, OpRef(mode="auto", seat=0))


def titan(s):
    return next(i for i in me(s).fleet if i.card == "3RIK02")


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


def enlist(s, name):
    """Enlist a Development by name through Strength of the Soul."""
    me(s).hand.append(s.new_inst("2ARC22"))
    refresh(s)
    play(s, card(s, "2ARC22", zone="hand"), 1)
    answer(s, "Development")
    answer(s, name)


NEEDS_OWN_SETUP = {
    ("3RIK07", 1),  # 3 Weapons beamed to a Ship at a neutral Location: test_proximity_blast_takes_control
}


@pytest.mark.parametrize("cid,index", [(cid, i) for cid in RIKER for i, op in enumerate(CARDS[cid].operations)
                                       if op.kind in ("PLAY", "ACTIVATION") and (cid, i) in registry.OPS])
def test_every_riker_operation_runs(cid, index):
    if (cid, index) in NEEDS_OWN_SETUP:
        pytest.skip("covered by its own test")
    kind = CARDS[cid].operations[index].kind
    tracks = {"research": 9, "influence": 9, "military": 9}
    if kind == "PLAY":
        position = {**RICH, "hand": RICH["hand"] + [cid, "2SHI01"], "tracks": tracks}  # a Ship to discard
    else:
        z = zone_for(cid)
        position = {**RICH, z: [cid] if z == "duty" else RICH.get(z, []) + [cid], "tracks": tracks}
    for seed in range(2):
        s = riker(**position)
        for ship in me(s).fleet:
            ship.at = s.neutral[0].uid
        me(s).captain.exhausted = cid == "3RIK15"  # for Deanna's "refresh your Captain"
        refresh(s)
        inst = card(s, cid, zone="hand" if kind == "PLAY" else zone_for(cid))
        if kind == "PLAY":
            assert can_play(s, inst, index), f"{cid} {index} not playable"
            play(s, inst, index)
        else:
            assert f"activate:{inst.uid}:{index}" in {o.id for o in s.decision.options}, f"{cid} {index} not offered"
            activate(s, inst, index)
        finish(s, seed)


def test_titan_shares_the_enterprise_operations():
    for index in range(3):
        assert registry.OPS[("3RIK02", index)].fn is registry.OPS[("3PIK19", index)].fn


# ------------------------------------------------------------------ Riker

def test_riker_swaps_a_card_for_one_of_the_same_suit():
    s = riker(empty_hand=True)
    me(s).hand.append(s.new_inst("2ARC15"))  # a Directive; Swooping In is a Directive in the Discard pile
    refresh(s)
    activate(s, me(s).captain, 0)
    resolve_all(s, prefer=("Swooping In",))
    assert me(s).draw[0].card == "2ARC15" and any(i.card == "3RIK23" for i in me(s).hand)


def test_riker_triggers_a_controlled_location_for_latinum():
    s = riker(locations=["3RIK22"], latinum=2)
    latinum = me(s).latinum
    refresh(s)
    activate(s, me(s).captain, 1)
    answer(s, "Starbase 25")
    answer(s, "Yes")  # spend 1 Latinum to trigger its CONTROL
    resolve_all(s, prefer=("No",))
    assert card(s, "3RIK22", zone="locations").away.get(0, 0) >= 1 and me(s).latinum == latinum - 1


# ------------------------------------------------------------------ Developments

def test_nepenthe_costs_a_deployed_ship_and_scores_with_research():
    s = riker(tracks={"military": 0})
    assert "3RIK03" in {i.card for i in _payable_developments(ctx(s))}
    enlist(s, "Nepenthe")
    answer(s, "U.S.S. Titan")
    resolve_all(s, prefer=("No",))
    assert any(i.card == "3RIK02" for i in me(s).log) and me(s).draw[0].card == "3RIK03"
    s2 = riker(tracks={"research": 9})
    assert registry.ENDGAME["3RIK03"](s2, me(s2)) == 3
    s3 = riker(tracks={"research": 8})
    assert registry.ENDGAME["3RIK03"](s3, me(s3)) == 0


def test_solving_science_mysteries_cost_and_passive():
    s = riker(tracks={"military": 7})
    me(s).dilithium, me(s).glory = 2, 0
    assert "3RIK04" not in {i.card for i in _payable_developments(ctx(s))}  # needs 7 // 2 = 3 Dilithium
    me(s).dilithium = 3
    assert "3RIK04" in {i.card for i in _payable_developments(ctx(s))}
    first = s.new_inst("3RIK16")  # Military icon
    me(s).duty.append(first)
    assert ctx(s).skills(first) == ["Military"]
    me(s).fleet.append(s.new_inst("3RIK04"))
    assert ctx(s).skills(first) == ["Research"]


def test_william_boimler_development_cost_beams_three_people():
    s = riker(dilithium=5, latinum=5, discard=["2PER07", "2PER11", "2PER14"])
    assert "3RIK05" in {i.card for i in _payable_developments(ctx(s))}
    enlist(s, "William Boimler")
    while s.decision.kind == "op":
        opts = options(s)
        answer(s, next((o for o in opts if "Discard pile" in o), opts[0]))
    assert len(titan(s).beamed) == 3


def test_william_boimler_support_after_exhausting_the_captain():
    s = riker(hand=["3RIK05", "3RIK16"])
    titan(s).beamed.append(s.new_inst("2PER07"))
    refresh(s)
    play(s, card(s, "3RIK16", zone="hand"), 0)
    while s.decision.kind == "op":
        opts = options(s)
        answer(s, "Hoshi Sato" if any("Hoshi" in o for o in opts) else ("No" if "No" in opts else opts[0]))
    assert me(s).captain.exhausted
    assert s.decision.kind == "trigger" and "William Boimler" in " ".join(options(s))


def test_william_boimler_hand_size():
    s = riker(duty=["3RIK05"])
    assert registry.HAND_SIZE["3RIK05"](s, me(s), 5) == 6


def test_utilize_logs_swooping_in():
    s = riker(dilithium=3, latinum=3)
    assert "3RIK08" in {i.card for i in _payable_developments(ctx(s))}
    enlist(s, "Utilize")
    resolve_all(s, prefer=("Swooping In", "No"))
    assert any(i.card == "3RIK23" for i in me(s).log)


def test_utilize_needs_swooping_in():
    s = riker(dilithium=3, latinum=3)
    me(s).discard = [i for i in me(s).discard if i.card != "3RIK23"]
    assert "3RIK08" not in {i.card for i in _payable_developments(ctx(s))}


# ------------------------------------------------------------------ Gluonic Distortion

def test_gluonic_distortion_enters_play_when_enlisted():
    s = riker(dilithium=3, staging=["2ENC08"])
    enlist(s, "Gluonic Distortion")
    resolve_all(s, prefer=("No",))
    assert any(i.card == "3RIK09" for i in me(s).status)
    assert game_view(s, 1)["players"][0]["draw"] is not None  # the face-up deck is public


def test_face_up_deck_lets_you_choose_what_to_draw():
    s = riker(hand=["2ARC15"])
    me(s).status.append(s.new_inst("3RIK09"))
    wanted = me(s).draw[-1]
    play(s, card(s, "2ARC15", zone="hand"), 0)  # Inspire: draw 2
    assert "face-up deck" in s.decision.prompt
    answer(s, CARDS[wanted.card].name)
    assert wanted.uid in uids(me(s).hand)


def test_gluonic_distortion_lifecycle():
    s = riker()
    me(s).status.append(s.new_inst("3RIK09"))
    run_op(s, "3RIK09", 0, "status")
    resolve_all(s)
    gd = card(s, "3RIK09", zone="status")
    assert gd.exhausted and any(CARDS[i.card].suit == "Incident" for i in me(s).hand)
    run_op(s, "3RIK09", 1, "status")
    resolve_all(s)
    assert any(i.card == "3RIK09" for i in me(s).log)


def test_without_gluonic_distortion_the_deck_is_hidden():
    s = riker()
    assert game_view(s, 1)["players"][0]["draw"] is None


# ------------------------------------------------------------------ Reserve and Available cards

def test_chateau_picard_glory_comes_from_the_supply():
    s = riker(staging=["3RIK10", "3RIK10"])
    glory, stardate = me(s).glory, s.stardate_glory
    inst = me(s).staging[0]
    start(s, OpRef(mode="op", seat=0, uid=inst.uid, card="3RIK10", index=2))
    resolve_all(s)
    assert me(s).glory == glory + 1 and s.stardate_glory == stardate


def test_holodeck_duplicates_and_rewards_nx01():
    s = riker(hand=["3RIK11", "3RIK16"], staging=["2ARC03"], dilithium=3)
    play(s, card(s, "3RIK11", zone="hand"), 1)
    assert any("First Officer" in o for o in options(s))
    answer(s, "First Officer")
    while s.decision.kind == "op" and "Gain 1 of which?" not in s.decision.prompt:
        answer(s, "No" if "No" in options(s) else options(s)[0])
    assert "Glory" in options(s)


def test_tactical_officer_counts_starfleet_people():
    s = riker(duty=["3RIK12"])
    officer = card(s, "3RIK12", zone="duty")
    assert ctx(s).skills(officer) == []
    me(s).duty += [s.new_inst("3RIK16"), s.new_inst("3RIK13")]
    assert ctx(s).skills(officer) == ["Military", "Military"]
    me(s).staging += [s.new_inst("3RIK14"), s.new_inst("3RIK15")]
    assert ctx(s).skills(officer) == ["Military"] * 3


def test_chief_engineer_arms_the_crew_while_exhausted():
    s = riker(duty=["3RIK13", "3RIK16"])
    first = card(s, "3RIK16", zone="duty")
    assert "Weapon" not in traits_of(s, first)
    card(s, "3RIK13", zone="duty").exhausted = True
    assert "Weapon" in traits_of(s, first)


def test_brad_boimler_spends_every_action():
    s = riker(hand=["3RIK14"])
    hand = len(me(s).hand)
    play(s, card(s, "3RIK14", zone="hand"), 0)
    resolve_all(s, prefer=("Do not",))
    assert me(s).actions == 0
    assert len(me(s).hand) >= hand - 1 + 3  # spent 3 actions: drew 4, free played at most 1


def test_brad_boimler_support_duplicates_a_promoted_person():
    s = riker(hand=["3RIK14", "3RIK16"], fleet=[])
    refresh(s)
    activate(s, titan(s), 3)  # promote First Officer from hand
    answer(s, "First Officer")
    assert s.decision.kind == "trigger" and "Brad Boimler" in " ".join(options(s))


def test_deanna_grants_incidents_a_play():
    s = riker(duty=["3RIK15"], hand=["2INC03"])
    incident = card(s, "2INC03", zone="hand")
    refresh(s)
    ids = {o.id for o in s.decision.options}
    assert f"play:{incident.uid}:100" in ids
    choose(s, 0, f"play:{incident.uid}:100", flag_irreversible=False)
    resolve_all(s)
    assert incident.uid not in uids(me(s).hand + me(s).staging)
    assert s.incident[-1].uid == incident.uid


def test_without_deanna_no_extra_play():
    s = riker(hand=["2INC03"])
    incident = card(s, "2INC03", zone="hand")
    refresh(s)
    assert f"play:{incident.uid}:100" not in {o.id for o in s.decision.options}


def test_deanna_looks_at_the_top_card():
    s = riker(hand=["3RIK15"])
    top = me(s).draw[0]
    play(s, card(s, "3RIK15", zone="hand"), 0)
    answer(s, "Log it")
    assert top.uid in uids(me(s).log)


def test_riker_maneuver_promotes_a_directive():
    s = riker(hand=["3RIK25"], duty=["3RIK16"])
    play(s, card(s, "3RIK25", zone="hand"), 0)
    resolve_all(s)
    maneuver = card(s, "3RIK25")
    assert maneuver in me(s).duty and maneuver.exhausted and me(s).captain.exhausted


def test_riker_maneuver_activation_then_dismiss():
    s = riker(duty=["3RIK25"], hand=["3RIK16"])
    refresh(s)
    latinum = me(s).latinum
    activate(s, card(s, "3RIK25", zone="duty"), 1)
    answer(s, "Gain 2 Latinum")
    answer(s, "Promote a Person")
    resolve_all(s)
    assert me(s).latinum == latinum + 2 and any(i.card == "3RIK16" for i in me(s).duty)
    assert any(i.card == "3RIK25" for i in me(s).discard)


def test_swooping_in_warps_to_a_controlled_location():
    s = riker(locations=["3RIK22"], hand=["3RIK23"])
    dil = me(s).dilithium
    play(s, card(s, "3RIK23", zone="hand"), 0)
    resolve_all(s)
    assert titan(s).at == card(s, "3RIK22", zone="locations").uid and me(s).dilithium == dil + 2


def test_proximity_blast_takes_control():
    s = riker(hand=["3RIK07"], tracks={"influence": 5})
    loc = s.neutral[0]
    titan(s).at = loc.uid
    titan(s).beamed += [s.new_inst("2CAR14"), s.new_inst("2CAR14"), s.new_inst("3PIK23")]  # Weapons
    refresh(s)
    assert can_play(s, card(s, "3RIK07", zone="hand"), 1)
    play(s, card(s, "3RIK07", zone="hand"), 1)
    resolve_all(s)
    assert loc.uid in uids(me(s).locations) and any(i.card == "3RIK07" for i in me(s).log)


def test_proximity_blast_dismisses_an_opponent_ship():
    s = riker(hand=["3RIK07"], opp={"fleet": ["2SHI01"]})
    loc = s.neutral[0]
    titan(s).at = loc.uid
    their = opp(s).fleet[-1]
    their.at = loc.uid
    refresh(s)
    play(s, card(s, "3RIK07", zone="hand"), 0)
    resolve_all(s, prefer=("No",))
    assert their.uid in uids(opp(s).discard)


# ------------------------------------------------------------------ missions

def _offered(s, mission):
    return f"mission:{mission}" in {o.id for o in s.decision.options}


def test_battling_the_pakled():
    s = riker(tracks={"military": 8, "influence": 4})
    refresh(s)
    assert _offered(s, "battling-the-pakled")
    glory = me(s).glory
    choose(s, 0, "mission:battling-the-pakled", flag_irreversible=False)
    resolve_all(s, prefer=("Dilithium", "No"))
    assert me(s).glory == glory  # only 2 of 3 criteria: no Glory


def test_battling_the_pakled_needs_two_criteria():
    s = riker(tracks={"military": 8})
    refresh(s)
    assert not _offered(s, "battling-the-pakled")


def test_spirit_of_starfleet():
    s = riker(board="advanced", duty=["3RIK16"], staging=["3RIK14", "3RIK14", "3RIK14", "3RIK04", "3RIK05"])
    refresh(s)
    assert _offered(s, "spirit-of-starfleet")
    choose(s, 0, "mission:spirit-of-starfleet", flag_irreversible=False)
    answer(s, "Vulcan")
    resolve_all(s)
    assert "spirit-of-starfleet" in me(s).missions_completed


def test_messages_from_old_friends():
    pilot_doctor = ["2PER10", "3PIK26", "3PIK23", "3PIK21"]  # Klingon, Pilot, Doctor, Scientist
    s = riker(board="advanced", staging=pilot_doctor)
    bottom = s.encounter[-1]
    refresh(s)
    assert _offered(s, "messages-from-old-friends")
    choose(s, 0, "mission:messages-from-old-friends", flag_irreversible=False)
    resolve_all(s)
    assert bottom.uid in uids(me(s).hand)
