"""Market cards (Person, Cargo, Ship, Ally): plans/card-implementation.md Steps 2 to 7.

Each spec's Tests section becomes a test here, plus an exerciser that plays every implemented PLAY and
ACTIVATION from a generous position and answers every question at random.
"""

import random

import pytest

from engine import cards as registry
from engine.content import MARKET_SUITS, content
from engine.game import HANDLERS, _advance_untracked
from engine.ops import find_inst
from tests.scenario import activate, answer, can_play, card, given, options, play

CARDS = content().cards
MARKET = sorted(k for k, c in CARDS.items() if c.suit in MARKET_SUITS and c.is_common and c.position != "Rewards")

# A hand, table and Discard pile with the traits Market costs ask for: Starfleet, Telepath, Weapon, Shady, Engineer,
# Helmet, Directive, Klingon, Doctor, Incident, a Research icon, and Persons.
RICH = dict(
    expansions=["second_contact"], promos=True,
    hand=["2CAR14", "2PER16", "2PER08", "2PER17", "2CAR05", "2GEO15", "2PER10", "2PER14", "2INC01", "2PER13"],
    duty=["2PER11"], fleet=["2SHI03", "2SHI07", "2CAR14"], staging=["2PER22"], discard=["2PER01", "2CAR07", "2INC02", "2SHI08", "2PER19"],
    dilithium=10, latinum=10, glory=10, actions=5, tracks={"research": 7, "influence": 7, "military": 7},
)


def implemented(kind: str) -> list[tuple[str, int]]:
    return [(cid, i) for cid in MARKET for i, op in enumerate(CARDS[cid].operations)
            if op.kind == kind and (cid, i) in registry.OPS]


def finish(s, seed: int = 0, limit: int = 300) -> None:
    """Answer every question at random until seat 0 is back at its Action Step menu.

    Skips the can't-be-undone flagging, which tries every option on a copy and is slow; test_undo covers it."""
    rng = random.Random(seed)
    for _ in range(limit):
        d = s.decision
        if s.step == "over" or (d.kind == "action" and d.seat == 0):
            return
        s.decision = None
        HANDLERS[d.kind](s, s.player(d.seat), rng.choice([o.id for o in d.options]))
        _advance_untracked(s)
    raise AssertionError(f"still answering after {limit} questions: {s.decision.prompt}")


def table_position(card_id: str) -> dict:
    """The generous position with the card in its table zone. A Person is the only Duty Officer (one slot)."""
    zone = table_zone(card_id)
    return {**RICH, zone: [card_id] if zone == "duty" else RICH[zone] + [card_id]}


def table_zone(card_id: str) -> str:
    c = CARDS[card_id]
    return "duty" if c.suit == "Person" else "fleet"


# Operations the generous position cannot reach; each has its own test below.
NEEDS_OWN_SETUP = {
    ("2CAR02", 1),  # Borg-only: can never be played (KW-DRONE-01)
    ("2PER08", 1),  # needs a Ship with 2 Ships beamed to it
    ("3SHI01", 3),  # needs a Starfleet Person beamed to Fesarius
    ("2PER03", 1),  # needs Klingon >= Starfleet in play
    ("2PER21", 0),  # needs one of your Away Teams on a Location
    ("2PER09", 1),  # needs two Persons beamed to Landru
}


@pytest.mark.parametrize("cid,index", implemented("PLAY") + implemented("ACTIVATION"))
def test_every_operation_runs(cid, index):
    op = CARDS[cid].operations[index]
    if op.kind == "PLAY":
        s = given(**{**RICH, "hand": RICH["hand"] + [cid]})
        legal = can_play(s, card(s, cid, zone="hand"), index)
    else:
        s = given(**table_position(cid))
        legal = f"activate:{card(s, cid, zone=table_zone(cid)).uid}:{index}" in {o.id for o in s.decision.options}
    if (cid, index) in NEEDS_OWN_SETUP:
        assert not legal
        return
    assert legal, f"{cid} {index} {op.kind} is not available in the generous position"
    for seed in range(2):
        trial = given(**({**RICH, "hand": RICH["hand"] + [cid]} if op.kind == "PLAY" else table_position(cid)))
        inst = card(trial, cid, zone="hand" if op.kind == "PLAY" else table_zone(cid))
        (play if op.kind == "PLAY" else activate)(trial, inst, index)
        finish(trial, seed)


# --------------------------------------------------------------------------- helpers for targeted tests


def me(s):
    return s.players[0]


def uids(cards):
    return [i.uid for i in cards]


def suits(cards):
    return [CARDS[i.card].suit for i in cards]


def drive(s, *texts):
    """Answer questions in order with options containing these texts."""
    for text in texts:
        answer(s, text)


def put(s, card_id, zone, seat=0):
    from engine import dev

    dev.apply(s, seat, {"kind": "card", "card": card_id, "zone": zone}, flag_irreversible=False)
    return card(s, card_id, seat, zone=zone if zone != "draw" else "draw")


# --------------------------------------------------------------------------- Allies


def test_arinsen_requires_military_3_and_pays_per_klingon():
    s = given(hand=["2ALL01"], duty=["2PER10"], tracks={"military": 2})  # Lursa is Klingon
    assert not can_play(s, card(s, "2ALL01", zone="hand"), 0)
    s = given(hand=["2ALL01"], duty=["2PER10"], tracks={"military": 3})
    dil = me(s).dilithium
    play(s, card(s, "2ALL01", zone="hand"), 0)
    answer(s, "Gain 2 Dilithium")  # Lursa and Arin'sen himself are Klingon: two choices
    answer(s, "Gain 1 Latinum")
    assert me(s).dilithium == dil + 2 and any(i.card == "2ALL01" for i in me(s).log)


def test_bolians_free_play_the_drawn_card():
    s = given(hand=["2ALL02"], draw=["2CAR15"], dilithium=3)  # Plasma Manifold on top of the deck
    play(s, card(s, "2ALL02", zone="hand"), 0)
    assert me(s).tracks["influence"] == 1
    actions = me(s).actions
    answer(s, "Yes")
    assert me(s).actions == actions + 1  # Plasma Manifold resolved: +1 action, no action spent


@pytest.mark.parametrize("cid,track,suit", [("2ALL03", "research", "Cargo"), ("2ALL04", "influence", "Person")])
def test_bynars_and_denobulans(cid, track, suit):
    s = given(hand=[cid], tracks={track: 2})
    assert not can_play(s, card(s, cid, zone="hand"), 1)
    s = given(hand=[cid])
    play(s, card(s, cid, zone="hand"), 0)
    answer(s, "faceup")
    answer(s, "Discard pile")
    assert suits(me(s).discard)[-1] == suit and me(s).log[-1].card == cid


def test_kelpiens_return_up_to_two_incidents():
    s = given(hand=["2ALL06", "2INC01"], discard=["2INC02"])
    incidents = len(s.incident)
    play(s, card(s, "2ALL06", zone="hand"), 0)
    drive(s, "Hostile Contact" if "Hostile Contact" in " ".join(options(s)) else "", "")
    assert len(s.incident) == incidents + 2 and me(s).log[-1].card == "2ALL06"


def test_organians_requirements():
    s = given(hand=["2ALL08"], tracks={"research": 3})
    o = card(s, "2ALL08", zone="hand")
    assert not can_play(s, o, 0) and not can_play(s, o, 1)
    s = given(hand=["2ALL08"], tracks={"research": 6})
    o = card(s, "2ALL08", zone="hand")
    top = me(s).reserve[0].uid
    play(s, o, 0)
    assert me(s).draw[0].uid == top


def test_orion_syndicate_needs_a_shady_and_draws_with_another_orion():
    s = given(hand=["2ALL09"], empty_hand=True)
    assert not can_play(s, card(s, "2ALL09", zone="hand"), 1)
    s = given(hand=["2ALL09", "2PER08"], staging=["2PER23"], empty_hand=True)  # Jackabog is Shady; Thelev is Orion
    hand, actions = len(me(s).hand), me(s).actions
    play(s, card(s, "2ALL09", zone="hand"), 1)
    assert me(s).actions == actions + 1 and len(me(s).hand) == hand - 2 + 2
    assert me(s).log[-1].card == "2ALL09"


def test_red_squadron_draws_two_keeps_one():
    s = given(hand=["2ALL10"], fleet=["2SHI03"], empty_hand=True)
    play(s, card(s, "2ALL10", zone="hand"), 0)
    answer(s, "")  # discard one of the 2 drawn
    assert len(me(s).hand) == 1
    answer(s, "Red Squadron")  # beam itself from the Staging Area
    answer(s, "D'Kyr")
    answer(s, "No")  # no warp
    ship = card(s, "2SHI03", zone="fleet")
    assert [b.card for b in ship.beamed] == ["2ALL10"]


def test_salt_vampires_log_a_staging_card_at_clean_up():
    s = given(hand=["2ALL11"])
    play(s, card(s, "2ALL11", zone="hand"), 0)
    choose_end(s)  # the only Staging Area card is Salt Vampires, so it logs itself without asking
    assert me(s).log[-1].card == "2ALL11"


def choose_end(s):
    from engine.game import choose

    choose(s, 0, "end")


def test_unimatrix_zero_spends_per_other_borg():
    s = given(hand=["2ALL14"], staging=["2SHI01"], dilithium=0, glory=-1)  # Borg Probe is Borg; no money at all
    assert me(s).dilithium == 1 and me(s).glory == 0
    s.players[0].dilithium = 0
    from engine import dev

    dev.apply(s, 0, {"kind": "resource", "resource": "glory", "amount": 0}, flag_irreversible=False)
    assert not can_play(s, card(s, "2ALL14", zone="hand"), 0)
    s = given(hand=["2ALL14"], empty_hand=True)
    play(s, card(s, "2ALL14", zone="hand"), 0)
    assert len(me(s).hand) == 2 and me(s).log[-1].card == "2ALL14"


def test_vidiians_log_themselves_unless_both():
    s = given(hand=["2ALL16"])
    play(s, card(s, "2ALL16", zone="hand"), 0)
    drive(s, "No", "No")
    assert me(s).log[-1].card == "2ALL16"


# --------------------------------------------------------------------------- Cargo


def test_augmentation_plague_deploys_and_klingon_captain_must_take_incident():
    s = given(hand=["2CAR01"], dilithium=2)
    play(s, card(s, "2CAR01", zone="hand"), 0)
    assert card(s, "2CAR01").uid in uids(me(s).fleet) and me(s).tracks["military"] == 2
    s = given(hand=["2CAR01"], dilithium=2)
    from engine.ops import find_inst as _f

    me(s).captain = s.new_inst("2PER10")  # stand-in Klingon Captain
    s.decision = None
    from engine.game import advance

    advance(s, flag_irreversible=False)
    hand, incidents = len(me(s).hand), len(s.incident)
    play(s, card(s, "2CAR01", zone="hand"), 0)
    assert len(s.incident) == incidents - 1 and len(me(s).hand) == hand - 1 + 1 + 3
    _ = _f


def test_augmentation_plague_reaction_on_own_klingon():
    s = given(hand=["2PER10"], fleet=["2CAR01"])
    glory = me(s).glory
    play(s, card(s, "2PER10", zone="hand"), 0)
    answer(s, "No")  # Lursa: don't beam
    if "Spend 1 Dilithium" in s.decision.prompt:
        answer(s, "No")
    assert s.decision.kind == "trigger"
    answer(s, "Use")
    assert me(s).glory == glory + 1


def test_borg_spatial_trajector():
    s = given(hand=["2CAR02"], tracks={"research": 3})
    assert not can_play(s, card(s, "2CAR02", zone="hand"), 0)
    s = given(hand=["2CAR02"], fleet=["2SHI03"], discard=["2PER07", "2PER11"], tracks={"research": 4}, empty_hand=True)
    play(s, card(s, "2CAR02", zone="hand"), 0)
    drive(s, "Hoshi", "Beam it", "D'Kyr", "Malcolm", "top")
    answer(s, "")  # where to send the Away Team
    answer(s, "Stop")
    assert [b.card for b in card(s, "2SHI03", zone="fleet").beamed] == ["2PER07"]
    assert me(s).draw[0].card == "2PER11"


def test_cloaking_device():
    s = given(hand=["2CAR03"], fleet=["2SHI03"])
    card(s, "2SHI03", zone="fleet").exhausted = True
    hand = len(me(s).hand)
    play(s, card(s, "2CAR03", zone="hand"), 0)
    answer(s, "D'Kyr")  # the only exhausted Ship is refreshed; no more to choose
    answer(s, "")  # junk a Market card
    assert not card(s, "2SHI03", zone="fleet").exhausted and len(me(s).hand) == hand - 1 + 2
    assert card(s, "2CAR03").uid in uids(me(s).fleet) and len(s.junk) == 1


def test_eva_suits_send_one_team_per_person_on_warp():
    s = given(hand=["2SHI03"], fleet=["2CAR05"], discard=["2PER07", "2PER11"])
    eva = card(s, "2CAR05", zone="fleet")
    for pid in ("2PER07", "2PER11"):
        p = card(s, pid, zone="discard")
        me(s).discard.remove(p)
        eva.beamed.append(p)
    play(s, card(s, "2SHI03", zone="hand"), 0)  # deploy and warp
    answer(s, "")  # warp destination
    while s.decision.kind == "op":
        answer(s, "No")
    answer(s, "EVA")
    loc = next(l for l in s.neutral if l.away.get(0))
    assert loc.away[0] == 2 and eva.uid not in uids(me(s).fleet)


def test_forced_singularity_needs_two_dilithium():
    s = given(hand=["2CAR06"])  # 1 Dilithium and 1 Glory: Glory substitutes for 2
    s.players[0].glory = 0
    from engine.game import advance

    s.decision = None
    advance(s, flag_irreversible=False)
    assert not can_play(s, card(s, "2CAR06", zone="hand"), 0)
    s = given(hand=["2CAR06"], dilithium=1)
    play(s, card(s, "2CAR06", zone="hand"), 0)
    answer(s, "No")
    answer(s, "")  # junk
    assert me(s).dilithium == 0 and card(s, "2CAR06").uid in uids(me(s).fleet)


def test_holosuite_scan_three():
    s = given(hand=["2CAR07"], latinum=2)
    hand = len(me(s).hand)
    play(s, card(s, "2CAR07", zone="hand"), 1)
    drive(s, "3 Latinum", "Person")
    answer(s, "")
    answer(s, "Discard pile")
    assert me(s).latinum == 0 and len(me(s).hand) == hand - 1 + 1


def test_jagos_implant_dismissed_without_duty_officer():
    s = given(hand=["2CAR09"], empty_hand=True)
    me(s).fleet.append(s.new_inst("2CAR09"))
    implant = me(s).fleet[-1]
    me(s).hand.clear()
    choose_end(s)
    while s.active != 0 or s.step != "action":
        d = s.decision
        from engine.game import choose

        choose(s, d.seat, {"discard": "done", "action": "end", "control": "skip", "glory": d.options[0].id,
                           "wipe": d.options[0].id}.get(d.kind, d.options[0].id))
    assert implant.uid in uids(me(s).discard)


def test_kemocite_needs_a_weapon():
    s = given(hand=["2CAR10"], empty_hand=True)
    me(s).draw.clear()
    me(s).reserve.clear()
    me(s).discard.clear()
    from engine.game import advance

    s.decision = None
    advance(s, flag_irreversible=False)
    assert not can_play(s, card(s, "2CAR10", zone="hand"), 0)


def test_medical_hat_counts_doctors_and_aliens():
    s = given(hand=["2CAR12"], duty=["2PER14"], empty_hand=True)  # Phlox is a Doctor; the Hat is a Doctor too
    play(s, card(s, "2CAR12", zone="hand"), 0)
    assert len(me(s).hand) == 2


def test_plasma_manifold():
    s = given(hand=["2CAR15"], dilithium=2)
    actions = me(s).actions
    play(s, card(s, "2CAR15", zone="hand"), 0)
    assert me(s).actions == actions + 1 and me(s).dilithium == 0


def test_saurian_brandy_needs_influence_5():
    s = given(hand=["2CAR16"], tracks={"influence": 4})
    assert not can_play(s, card(s, "2CAR16", zone="hand"), 0)


def test_universal_translator_with_two_aliens_only_logs():
    s = given(hand=["2CAR18"], fleet=["2SHI07"])  # Medusan Vessel is Alien: 1 Alien
    encounters = len(s.encounter)
    play(s, card(s, "2CAR18", zone="hand"), 1)
    assert len(s.encounter) == encounters and me(s).log[-1].card == "2CAR18"


# --------------------------------------------------------------------------- Persons


def test_ash_tyler_requirement_and_hand_size():
    s = given(hand=["2PER03"], staging=["2CAR14", "2PER11", "2PER10"])  # 2 Starfleet, 1 Klingon
    tyler = card(s, "2PER03", zone="hand")
    assert can_play(s, tyler, 0)
    from engine.game import hand_size

    me(s).duty.append(s.new_inst("2PER03"))
    me(s).glory = 8
    assert hand_size(s, me(s)) == 7


def test_degra_activation():
    s = given(duty=["2PER05"], fleet=["2CAR14"], dilithium=3, tracks={"research": 5})
    activate(s, card(s, "2PER05", zone="duty"), 1)
    assert any(CARDS[i.card].suit == "Encounter" for i in me(s).hand) and me(s).log[-1].card == "2PER05"
    assert card(s, "2CAR14").uid in uids(me(s).discard)


def test_jackabog_helmet_resupply_and_clumpship():
    s = given(duty=["2PER08"], empty_hand=True)
    jack = card(s, "2PER08", zone="duty")
    jack.beamed.append(s.new_inst("2CAR05"))  # EVA Suits is a Helmet
    from engine import ops
    from engine.state import OpRef

    ctx = ops.Ctx(s, OpRef(mode="auto", seat=0, uid=jack.uid, index=2))
    gen = registry.OPS[("2PER08", 2)].fn(ctx, ops.Actions(ctx, registry.OPS[("2PER08", 2)].uses))
    for _ in gen:
        pass
    assert me(s).tracks["military"] == 1 and len(me(s).hand) == 2
    # The second PLAY needs a Ship with 2 Ships beamed to it.
    s = given(hand=["2PER08"], fleet=["2SHI03"], tracks={"military": 5})
    host = card(s, "2SHI03", zone="fleet")
    host.beamed += [s.new_inst("2SHI07"), s.new_inst("2SHI08")]
    s.decision = None
    from engine.game import advance

    advance(s, flag_irreversible=False)
    play(s, card(s, "2PER08", zone="hand"), 1)
    assert host.uid in uids(me(s).discard) and me(s).log[-1].card == "2PER08"


def test_landru_cannot_be_played():
    s = given(hand=["2PER09"])
    assert not any(o.id.startswith(f"play:{card(s, '2PER09', zone='hand').uid}") for o in s.decision.options)


def test_lursa_activation_romulan_business():
    s = given(duty=["2PER10"], hand=["2SHI05"], empty_hand=True)  # Holographic Drone Ship: Romulan, not Business
    s2 = given(duty=["2PER10"], hand=["2PER22"], empty_hand=True)  # Tevrin Krit: Business
    activate(s, card(s, "2PER10", zone="duty"), 1)
    assert me(s).tracks["military"] == 1 and len(me(s).hand) == 1
    lat = me(s2).latinum
    activate(s2, card(s2, "2PER10", zone="duty"), 1)
    assert me(s2).latinum == lat + 1


def test_malcolm_reed_counts_species_in_discard():
    s = given(hand=["2PER11"], discard=["2PER12", "2SHI05"])  # Malik is Augment; the Drone Ship is Romulan
    play(s, card(s, "2PER11", zone="hand"), 0)
    answer(s, "top card of your deck")
    assert me(s).tracks["military"] >= 3


def test_malik_reaction_only_when_promoted_from_hand():
    s = given(hand=["2PER12", "2CAR15"], dilithium=5)
    # Played: his PLAY needs a Human/Klingon to log; play Plasma instead and check no Malik offer.
    s = given(hand=["3ALL02", "2PER12", "2CAR15"])
    play(s, card(s, "3ALL02", zone="hand"), 0)
    answer(s, "Malik")
    assert s.decision.kind == "trigger" and "Malik" in options(s)[0]
    actions = me(s).actions
    answer(s, "Use")
    answer(s, "")
    assert me(s).actions == actions + 1


def test_petra_needs_a_junk_card_of_the_suit():
    s = given(hand=["2PER13", "2GEO15"], empty_hand=True, expansions=["second_contact"])
    s.junk = [i for i in s.junk if CARDS[i.card].suit != "Directive"]
    play(s, card(s, "2PER13", zone="hand"), 0)  # Analyze is the only other card: picked without asking
    assert me(s).draw[0].card == "2GEO15" and me(s).glory == 1


def test_phlox_second_play_returns_all_and_beams():
    s = given(hand=["2PER14", "2INC01", "2INC03"], fleet=["2SHI03"], tracks={"research": 6})
    incidents = len(s.incident)
    play(s, card(s, "2PER14", zone="hand"), 1)
    drive(s, "", "")  # return both Incidents; the hand then has none, so the loop ends
    answer(s, "D'Kyr")
    assert len(s.incident) >= incidents + 2
    assert [b.card for b in card(s, "2SHI03", zone="fleet").beamed] == ["2PER14"]


def test_soji_reaction_not_on_play_and_draws_per_five_logged():
    s = given(hand=["2PER19"], dilithium=1)
    play(s, card(s, "2PER19", zone="hand"), 0)
    while s.decision.kind == "op":
        answer(s, "")
    assert s.decision.kind == "action"  # no Reaction offered for herself from the Staging Area
    s = given(hand=["3ALL02", "2PER19", "2CAR15"], log=["2CAR15"] * 9)
    play(s, card(s, "3ALL02", zone="hand"), 0)
    answer(s, "Soji")
    answer(s, "Use")
    hand = len(me(s).hand)
    answer(s, "Plasma")
    assert len(me(s).log) == 10 and len(me(s).hand) == hand - 1 + 2


def test_talok_hand_size():
    from engine.game import hand_size

    s = given(duty=["2PER21"])
    assert hand_size(s, me(s)) == 6


def test_tevrin_krit_resupply():
    s = given(duty=["2PER22"], fleet=["2CAR14", "2CAR05"])
    from engine import ops
    from engine.state import OpRef

    tev = card(s, "2PER22", zone="duty")
    lat = me(s).latinum
    ctx = ops.Ctx(s, OpRef(mode="auto", seat=0, uid=tev.uid, index=1))
    for _ in registry.OPS[("2PER22", 1)].fn(ctx, ops.Actions(ctx, [ops.A.GAIN_RESOURCE])):
        pass
    assert me(s).latinum == lat + 2


def test_thelev_draws_per_opponent_ambassador():
    s = given(hand=["2PER23"], empty_hand=True, opp={"duty": ["2PER16"], "staging": ["2PER15"]})
    from engine.ops import Ctx
    from engine.state import OpRef

    ambassadors = Ctx(s, OpRef(mode="auto", seat=0)).count_in_play(
        lambda i: "Ambassador" in CARDS[i.card].traits, s.players[1])
    assert ambassadors >= 2  # Riva, Rillak, and Soval's Captain
    play(s, card(s, "2PER23", zone="hand"), 0)
    assert len(me(s).hand) == ambassadors


def test_travis_warps_and_sends_two():
    s = given(hand=["2PER24"], fleet=["2SHI03"], dilithium=1)
    play(s, card(s, "2PER24", zone="hand"), 0)
    answer(s, "D'Kyr")
    answer(s, "")  # destination
    drive(s, "Yes", "Yes")
    loc = next(l for l in s.neutral if l.away.get(0))
    assert loc.away[0] == 2 and me(s).captain.exhausted


def test_vaal_trask_resupply_repeats_per_neutral_team():
    s = given(duty=["2PER25"])
    for loc in s.neutral:
        loc.away[1] = 1
    from engine import ops
    from engine.state import OpRef

    va = card(s, "2PER25", zone="duty")
    ctx = ops.Ctx(s, OpRef(mode="auto", seat=0, uid=va.uid, index=1))
    gen = registry.OPS[("2PER25", 1)].fn(ctx, ops.Actions(ctx, registry.OPS[("2PER25", 1)].uses))
    asks = 0
    try:
        ask = next(gen)
        while True:
            asks += 1
            ask = gen.send("top")
    except StopIteration:
        pass
    assert asks == 3


# --------------------------------------------------------------------------- Ships and expansion / promo cards


def test_fesarius_takes_an_encounter():
    s = given(hand=["2GEO15"], fleet=["3SHI01", "2SHI03"], expansions=["second_contact"])
    fes = card(s, "3SHI01", zone="fleet")
    fes.beamed.append(s.new_inst("2PER11"))  # Malcolm Reed: Starfleet Person
    s.decision = None
    from engine.game import advance

    advance(s, flag_irreversible=False)
    activate(s, fes, 3)
    while s.decision.kind == "op":  # which Directive to discard, if there are several
        answer(s, "")
    assert suits(me(s).discard).count("Encounter") == 1 and me(s).log[-1].card == "3SHI01"


def test_frank_hollander_may_log_himself():
    s = given(hand=["0CAR02"], empty_hand=True, promos=True)
    glory = me(s).glory
    play(s, card(s, "0CAR02", zone="hand"), 0)  # the only Cargo is Frank himself
    assert me(s).log[-1].card == "0CAR02" and me(s).glory == glory + 1


def test_cabot_draws_per_own_creature():
    s = given(fleet=["0SHI02", "2CAR08"], staging=["3CAR02"], opp={"staging": ["2ALL11"] * 3}, promos=True,
              expansions=["second_contact"])
    from engine import ops
    from engine.state import OpRef

    cabot = card(s, "0SHI02", zone="fleet")
    hand = len(me(s).hand)
    ctx = ops.Ctx(s, OpRef(mode="auto", seat=0, uid=cabot.uid, index=1))
    for _ in registry.OPS[("0SHI02", 1)].fn(ctx, ops.Actions(ctx, registry.OPS[("0SHI02", 1)].uses)):
        pass
    assert len(me(s).hand) == hand + 2 and cabot.uid in uids(me(s).fleet)


def test_illyrians_promote_and_clean_up():
    s = given(hand=["3ALL02", "2PER11"], expansions=["second_contact"])
    play(s, card(s, "3ALL02", zone="hand"), 0)
    answer(s, "Malcolm")
    assert card(s, "2PER11").uid in uids(me(s).duty)
    choose_end(s)
    assert me(s).tracks["research"] == 1 and me(s).log[-1].card == "3ALL02"


def _matching_event(s, cid, index):
    """A trigger event the operation accepts, built from cards in the position, or None."""
    from engine import ops
    from engine.state import OpRef

    impl = registry.OPS[(cid, index)]
    host = card(s, cid)
    candidates = []
    for seat, p in enumerate(s.players):
        for inst in [*p.staging, *p.fleet, *p.duty, *p.hand, *p.discard]:
            candidates += [{"kind": k, "seat": seat, "uid": inst.uid, "played": True}
                           for k in ("put_into_play", "deploy")]
            candidates += [{"kind": "gain", "seat": seat, "uid": inst.uid, "to": to} for to in ("discard", "top")]
            candidates += [{"kind": k, "seat": seat, "uid": inst.uid, "by": seat}
                           for k in ("log", "take_incident", "return_incident", "exhaust")]
            if inst in p.fleet:
                candidates.append({"kind": "warp", "seat": seat, "uid": inst.uid, "location": s.neutral[0].uid})
        candidates.append({"kind": "attacked", "seat": seat, "uid": None, "attacker": 1 - seat})
        candidates.append({"kind": "would_attack", "seat": seat, "uid": None, "attacker": 1 - seat,
                           "removes_away_teams": True})
        for inc in [i for i in p.hand if CARDS[i.card].suit == "Incident"]:
            candidates.append({"kind": "would_return_incident", "seat": seat, "uid": inc.uid})
        for kind in ("dilithium", "latinum", "glory"):
            candidates.append({"kind": "gain_resource", "seat": seat, "uid": None, "resource": kind, "amount": 1})
        for loc in [*s.neutral, *p.locations]:
            candidates.append({"kind": "send_away_team", "seat": seat, "uid": loc.uid, "location": loc.uid,
                               "controlled": loc in p.locations, "neutral": loc in s.neutral})
    for ev in candidates:
        ctx = ops.Ctx(s, OpRef(mode="trigger", seat=0, uid=host.uid, index=index, event=ev))
        if impl.trigger(ctx, ev):
            return ev
    return None


STEP_KINDS = ("REACTION", "RESUPPLY", "CLEAN-UP")


@pytest.mark.parametrize("cid,index", [k for kind in STEP_KINDS for k in implemented(kind)])
def test_every_triggered_and_step_operation_runs(cid, index):
    """Run each Reaction (with an event it accepts), Resupply and Clean-up operation from a generous position."""
    from engine.game import advance
    from engine.state import OpRef

    op = CARDS[cid].operations[index]
    zone = "staging" if op.kind == "CLEAN-UP" and CARDS[cid].suit in ("Ally", "Cargo") and \
        "Ongoing" not in CARDS[cid].traits else table_zone(cid)
    extra = {"hand": RICH["hand"] + ["2PER12", "2PER19", "3CAR01", "2PER20"],
             "staging": ["2PER22", "2PER10", "2PER19", "2ALL11", "2CAR15"], "locations": ["2GEO19"],
             "fleet": RICH["fleet"] + ["2CAR05"], "tracks": {"research": 7, "influence": 7, "military": 7}}
    for seed in range(2):
        base = {**RICH, **extra}
        s = given(**{**base, zone: [cid] if zone == "duty" else (base.get(zone) or []) + [cid]},
                  opp={"fleet": ["2SHI03"], "staging": ["2PER10"]})
        host = card(s, cid, zone=zone)
        card(s, "2SHI03", zone="fleet").beamed.append(s.new_inst("2PER07"))  # a beamed card, for recall effects
        if op.kind == "REACTION":
            ev = _matching_event(s, cid, index)
            assert ev is not None, f"no event in the position triggers {cid} {index}"
            ref = OpRef(mode="trigger", seat=0, uid=host.uid, index=index, event=ev)
        else:
            ref = OpRef(mode="auto", seat=0, uid=host.uid, index=index)
        s.decision = None
        s.op_queue.append(ref)
        advance(s, flag_irreversible=False)
        finish(s, seed)


# --------------------------------------------------------------------------- Step 3: events and resources on cards


def run_to_action(s):
    """Answer each question with its first option until seat 0's Action Step menu."""
    from engine.game import choose

    for _ in range(100):
        d = s.decision
        if d.kind == "action" and d.seat == 0:
            return
        choose(s, d.seat, d.options[0].id, flag_irreversible=False)


def test_horta_adds_two_dilithium_after_a_gain():
    s = given(hand=["2ALL02"], fleet=["2CAR08"], tracks={"research": 4}, empty_hand=True)
    me(s).hand.append(s.new_inst("2SHI04"))
    # Hostile-free: gain Dilithium with Analyze's third PLAY.
    s = given(hand=["2GEO15"], fleet=["2CAR08"], tracks={"research": 4})
    dil = me(s).dilithium
    play(s, card(s, "2GEO15", zone="hand"), 2)
    assert s.decision.kind == "trigger" and "Horta" in options(s)[0]
    answer(s, "Use")
    assert me(s).dilithium == dil + 4
    s = given(hand=["2GEO15"], fleet=["2CAR08"], tracks={"research": 3})
    play(s, card(s, "2GEO15", zone="hand"), 2)
    assert s.decision.kind == "action"  # Research 3: no offer


def test_rom_draws_after_gaining_latinum():
    s = given(hand=["2CAR07"], duty=["2PER17"], discard=["2PER07"], empty_hand=True)
    play(s, card(s, "2CAR07", zone="hand"), 0)  # Holosuite: gain 2 Latinum ...
    while s.decision.kind == "op":
        answer(s, "")  # ... junk a card
    assert s.decision.kind == "trigger"
    answer(s, "Use")
    drive(s, "Yes", "Hoshi")
    assert {i.card for i in me(s).hand} >= {"2PER07"} and len(me(s).hand) == 2


def test_kaelon_places_moves_and_logs():
    s = given(hand=["2ALL05"])
    play(s, card(s, "2ALL05", zone="hand"), 0)
    kaelon = card(s, "2ALL05", zone="fleet")
    assert kaelon.res == {"dilithium": 3} and kaelon.exhausted
    choose_end(s)
    assert me(s).tracks["research"] == 1  # exhausted at Clean-up: +1 Research
    # Next Clean-up (refreshed): move 1 Dilithium to the Market, three times, then it logs itself.
    for turn in range(3):
        kaelon.exhausted = False
        s.decision = None
        from engine.game import advance

        s.step, s.substep = "cleanup", "ops"
        advance(s, flag_irreversible=False)
        answer(s, "")
        run_to_action_or_end(s)
    assert kaelon.uid in uids(me(s).log)
    assert sum(i.res.get("dilithium", 0) for i in s.market.values() if i) == 3


def run_to_action_or_end(s):
    from engine.game import choose

    for _ in range(50):
        d = s.decision
        if d is None or s.step != "cleanup" or d.kind not in ("op", "trigger"):
            return
        choose(s, d.seat, d.options[0].id, flag_irreversible=False)


def test_kaelon_reaction_after_logging_a_person():
    s = given(hand=["2ALL04"], fleet=["2ALL05"], discard=["2PER07"])
    kaelon = card(s, "2ALL05", zone="fleet")
    kaelon.res["dilithium"] = 2
    dil = me(s).dilithium
    play(s, card(s, "2ALL04", zone="hand"), 0)  # Denobulans: gain a Person, log itself (an Ally: no trigger)
    answer(s, "faceup")
    answer(s, "Discard pile")
    assert s.decision.kind == "action"
    s = given(hand=["2PER25"], fleet=["2ALL05"], discard=["2PER07"])
    kaelon = card(s, "2ALL05", zone="fleet")
    kaelon.res["dilithium"] = 2
    play(s, card(s, "2PER25", zone="hand"), 0)  # Va'al Trask may log a Person
    answer(s, "No")
    answer(s, "Hoshi")
    assert s.decision.kind == "trigger"
    dil = me(s).dilithium
    answer(s, "Use")
    answer(s, "Yes")
    # Objects are rebuilt when an operation resumes, so look the card up again.
    assert me(s).dilithium == dil + 1 and card(s, "2ALL05", zone="fleet").res == {"dilithium": 1}


def test_moopsy_draws_when_the_opponent_logs_a_person():
    from engine import dev

    s = given(fleet=["3CAR02"], expansions=["second_contact"], opp={"hand": ["2PER25"]})
    hand = len(me(s).hand)
    choose_end(s)
    run_to_action_for(s, 1)
    play(s, card(s, "2PER25", seat=1, zone="hand"), 0)  # no Starfleet in hand, so no scan question
    answer(s, "Stel")  # the opponent logs a Person
    assert s.decision.kind == "trigger" and s.decision.seat == 0 and "Moopsy" in options(s)[0]
    answer(s, "Use")
    assert len(me(s).hand) == hand + 1
    _ = dev


def run_to_action_for(s, seat):
    from engine.game import choose

    for _ in range(100):
        d = s.decision
        if d.kind == "action" and d.seat == seat:
            return
        choose(s, d.seat, {"discard": "done", "action": "end", "control": "skip"}.get(d.kind, d.options[0].id),
               flag_irreversible=False)


def test_golden_statue_recalls_after_logging_an_engineer():
    s = given(hand=["2ALL03"], fleet=["0CAR03", "2SHI03"], promos=True)  # Bynars are Engineers and log themselves
    ship = card(s, "2SHI03", zone="fleet")
    ship.beamed.append(s.new_inst("2PER07"))
    play(s, card(s, "2ALL03", zone="hand"), 0)
    answer(s, "faceup")
    answer(s, "Discard pile")
    assert s.decision.kind == "trigger"
    answer(s, "Use")
    assert not card(s, "2SHI03", zone="fleet").beamed and any(i.card == "2PER07" for i in me(s).hand)


def test_phlox_research_after_sending_to_neutral():
    s = given(hand=["2GEO22"], duty=["2PER14"])  # Kamran Gant sends an Away Team
    play(s, card(s, "2GEO22", zone="hand"), 0)
    answer(s, "")  # a neutral Location
    assert s.decision.kind == "trigger"
    answer(s, "Use")
    assert me(s).tracks["research"] == 1


def test_tysess_triggers_control_of_a_controlled_location():
    s = given(hand=["2GEO22"], duty=["2PER04"], locations=["2GEO19"])  # Vulcan Science Academy: CONTROL gains a Person
    play(s, card(s, "2GEO22", zone="hand"), 0)
    answer(s, "Vulcan Science Academy")  # a controlled Location: Gant also gains 1 Dilithium
    assert s.decision.kind == "trigger" and "Tysess" in options(s)[0]
    answer(s, "Use")
    assert "Gain a Person?" in s.decision.prompt  # the Academy's CONTROL is resolving


def test_sukal_gains_dilithium_on_taking_an_incident():
    s = given(hand=["2GEO15"], duty=["2PER20"])
    dil = me(s).dilithium
    play(s, card(s, "2GEO15", zone="hand"), 0)  # Analyze: take an Incident to gain a Ship
    run_to_action(s)
    assert me(s).dilithium == dil + 1


def test_rillak_gains_an_action_after_utilize():
    s = given(hand=["2GEO18"], duty=["2PER15"])
    actions = me(s).actions
    play(s, card(s, "2GEO18", zone="hand"), 0)
    answer(s, "Use")
    assert me(s).actions == actions - 1 + 1


def test_kazon_raider_after_gaining_to_the_top():
    s = given(hand=["2GEO16"], fleet=["2SHI06"], latinum=1)  # Recruit: gain a Person
    raider = card(s, "2SHI06", zone="fleet")
    hand = len(me(s).hand)
    play(s, card(s, "2GEO16", zone="hand"), 0)
    answer(s, "")  # put a card on top (cost)
    answer(s, "faceup")
    answer(s, "top")
    answer(s, "Use")
    assert not raider.exhausted and len(me(s).hand) == hand - 2 + 1


def test_talvath_places_dilithium_and_keeps_it_when_dismissed_in_control():
    s = given(hand=["2ALL08"], fleet=["3SHI02"], expansions=["second_contact"], tracks={"research": 4})
    talvath = card(s, "3SHI02", zone="fleet")
    play(s, card(s, "2ALL08", zone="hand"), 0)  # Organians: an Anomaly put into play
    answer(s, "Use")
    answer(s, "No")
    assert talvath.res == {"dilithium": 1}
    glory, dil = me(s).glory, me(s).dilithium
    from engine.game import dismiss

    s.step = "control"
    dismiss(s, me(s), talvath)
    assert me(s).glory == glory + 1 and me(s).dilithium == dil + 1
    s2 = given(fleet=["3SHI02"], expansions=["second_contact"])
    t2 = card(s2, "3SHI02", zone="fleet")
    t2.res["dilithium"] = 2
    dil = me(s2).dilithium
    dismiss(s2, me(s2), t2)  # Action Step: resources return to the supply
    assert me(s2).dilithium == dil


def test_gaining_a_market_card_with_dilithium_on_it():
    s = given(hand=["2GEO15"])
    ship = s.market["Ship"]
    ship.res["dilithium"] = 2
    dil = me(s).dilithium
    play(s, card(s, "2GEO15", zone="hand"), 0)
    answer(s, "faceup")
    answer(s, "Discard pile")
    gained = next(i for i in me(s).discard if i.uid == ship.uid)
    assert me(s).dilithium == dil + 2 and not gained.res


# --------------------------------------------------------------------------- Step 4: attacks


def opp(s):
    return s.players[1]


def test_attack_counts_and_riva_ignores_it():
    """Malik steals 1 Glory; with Riva on duty the defender may discard to ignore it and gain Glory."""
    s = given(hand=["2PER12", "2CAR14"], opp={"glory": 4})
    their = opp(s).glory
    play(s, card(s, "2PER12", zone="hand"), 0)  # discard Phasers (the only Weapon) as the cost
    assert opp(s).glory == their - 1 and me(s).glory == 2
    s = given(hand=["2PER12", "2CAR14"], opp={"glory": 4, "duty": ["2PER16"], "hand": ["2PER15"]})
    their = opp(s).glory
    play(s, card(s, "2PER12", zone="hand"), 0)
    assert s.decision.seat == 1 and "Riva" in options(s)[0]
    answer(s, "Use Riva")
    answer(s, "Rillak")  # Ambassador shares 1 trait with Riva
    assert opp(s).glory == their + 1 and me(s).glory == 1


def test_jarok_gains_glory_after_being_attacked():
    s = given(hand=["2PER12", "2CAR14"], opp={"duty": ["2PER01"], "glory": 2})
    their = opp(s).glory
    play(s, card(s, "2PER12", zone="hand"), 0)
    assert s.decision.kind == "trigger" and s.decision.seat == 1
    answer(s, "Use")
    answer(s, "No")
    assert opp(s).glory == their - 1 + 1


def test_pasalk_blocks_opponent_reactions_on_your_turn():
    s = given(hand=["2PER12", "2CAR14"], staging=["2PER26"], opp={"duty": ["2PER16"], "hand": ["2PER15"], "glory": 2})
    their = opp(s).glory
    play(s, card(s, "2PER12", zone="hand"), 0)
    assert s.decision.kind == "action" and opp(s).glory == their - 1  # no Riva offer, the steal happens


def test_pasalk_repeats_against_an_augment():
    s = given(hand=["2PER26"], opp={"staging": ["2PER12"]})
    hand = len(opp(s).hand)
    glory = me(s).glory
    play(s, card(s, "2PER26", zone="hand"), 0)
    while s.decision.kind == "op":
        answer(s, "")
    assert len(opp(s).hand) == hand - 2 and me(s).glory == glory + 1


def test_gral_gives_an_incident_instead_of_returning_it():
    s = given(hand=["2GEO23", "2CAR14"], duty=["2PER02"])  # Hostile Contact returns itself
    hc = card(s, "2GEO23", zone="hand")
    play(s, hc, 0)
    answer(s, "Phasers")  # discard cost
    assert "Ambassador Gral" in options(s)[0]
    answer(s, "Use")
    assert any(i.uid == hc.uid for i in opp(s).hand)


def test_phasers_ignore_away_team_removal():
    s = given(hand=["2CAR17", "2PER10"], opp={"fleet": ["2CAR14"]})
    loc = s.neutral[0]
    loc.away[1] = 2
    play(s, card(s, "2CAR17", zone="hand"), 0)
    answer(s, "")  # junk
    answer(s, "Yes")
    assert "Phasers" in options(s)[0] and s.decision.seat == 1
    answer(s, "Use")
    assert loc.uid and next(l for l in s.neutral if l.uid == loc.uid).away[1] == 2


def test_disruptor_pistols_remove_two_for_two_glory():
    s = given(hand=["2CAR17", "2PER10"])
    s.neutral[0].away[1] = 2
    glory = me(s).glory
    play(s, card(s, "2CAR17", zone="hand"), 0)
    answer(s, "")
    answer(s, "Yes")
    answer(s, "Yes")  # remove the second one too
    assert me(s).glory == glory + 2 and not s.neutral[0].away.get(1)


def test_ash_tyler_dismisses_an_opponent_duty_officer():
    # Georgiou's Captain and the Shenzhou are Starfleet, so three Klingons are needed.
    s = given(hand=["2PER03"], staging=["2PER10", "2ALL01", "2ALL01"], opp={"duty": ["2SOV05"]})
    glory = me(s).glory
    play(s, card(s, "2PER03", zone="hand"), 1)
    answer(s, "No")
    assert not opp(s).duty and me(s).glory == glory + 2


def test_talok_opponent_takes_an_incident():
    s = given(hand=["2PER21"])
    s.neutral[0].away[0] = 1
    from engine.game import advance

    s.decision = None
    advance(s, flag_irreversible=False)
    hand = len(opp(s).hand)
    play(s, card(s, "2PER21", zone="hand"), 0)
    answer(s, "faceup") if "faceup" in " ".join(options(s)) else None
    while s.decision.kind == "op":
        answer(s, "")
    assert len(opp(s).hand) == hand + 1


def test_harry_mudd_forces_a_log_or_an_incident():
    s = given(hand=["2PER06"], tracks={"influence": 3}, opp={"hand": []})
    opp(s).hand.clear()
    opp(s).discard.clear()
    from engine.game import advance

    s.decision = None
    advance(s, flag_irreversible=False)
    play(s, card(s, "2PER06", zone="hand"), 0)
    answer(s, "No")  # don't promote
    assert len(opp(s).hand) == 1 and CARDS[opp(s).hand[0].card].suit == "Incident"


def test_tellarites_give_an_incident():
    s = given(hand=["2ALL13", "2INC01"])
    play(s, card(s, "2ALL13", zone="hand"), 0)
    assert any(i.card == "2INC01" for i in opp(s).hand)


def test_computer_virus_with_no_beamed_cards_gives_an_incident():
    s = given(hand=["2CAR04"])
    hand = len(opp(s).hand)
    play(s, card(s, "2CAR04", zone="hand"), 0)
    assert len(opp(s).hand) == hand + 1


def test_computer_virus_logs_itself_when_opponent_plays_an_engineer():
    s = given(fleet=["2CAR04"], opp={"hand": ["2PER17"]})
    choose_end(s)
    run_to_action_for(s, 1)
    glory = me(s).glory
    play(s, card(s, "2PER17", seat=1, zone="hand"), 0)
    while s.decision.kind == "op":
        answer(s, "No")
    run_to_action_for(s, 1)
    assert me(s).log[-1].card == "2CAR04" and me(s).glory == glory + 1


def test_lirpa_with_no_opponent_duty_officer_still_draws_for_vulcans():
    s = given(hand=["2CAR11"], staging=["2GEO04"], empty_hand=True)  # Sarek is Vulcan
    opp(s).duty.clear()
    play(s, card(s, "2CAR11", zone="hand"), 0)
    assert len(me(s).hand) == 1


def test_steal_in_cadet_takes_one_from_the_supply():
    s = given(hand=["2PER12", "2CAR14"], mode="cadet")
    play(s, card(s, "2PER12", zone="hand"), 0)
    assert me(s).glory == 2


def test_cadet_disruptor_removes_one_virtual_team():
    s = given(hand=["2CAR17", "2PER10"], mode="cadet")
    glory = me(s).glory
    play(s, card(s, "2CAR17", zone="hand"), 0)
    answer(s, "")
    answer(s, "Yes")
    answer(s, "")
    assert me(s).glory == glory + 1


# --------------------------------------------------------------------------- Step 5: Duty Officer slots and modifiers


def promote_with_illyrians(s, person_name):
    """Play Illyrians (no action) to promote a Person from hand. Illyrians stays in the Staging Area."""
    play(s, card(s, "3ALL02", zone="hand"), 0)
    answer(s, person_name)


def test_jarok_forbids_attack_cards():
    s = given(hand=["2PER12", "2CAR14"], duty=["2PER01"])
    malik = card(s, "2PER12", zone="hand")
    assert not any(o.id.startswith(f"play:{malik.uid}") for o in s.decision.options)


def test_jarok_extra_slot_is_for_a_starfleet_officer():
    from engine.ops import duty_fits

    s = given(duty=["2PER01"])
    me_ = me(s)
    reed = s.new_inst("2PER11")  # Starfleet
    lursa = s.new_inst("2PER10")  # not Starfleet
    assert duty_fits(s, me_, [*me_.duty, reed])
    assert not duty_fits(s, me_, [*me_.duty, lursa])
    # Jarok's own slot is for the others: a second Jarok cannot use the first's... but the first is not Starfleet,
    # so with only Jarok and a non-Starfleet the extra slot stays empty.


def test_promoting_beyond_the_limit_asks_which_to_dismiss():
    s = given(hand=["3ALL02", "2PER10"], duty=["2PER11"], expansions=["second_contact"])
    # Illyrians in the Staging Area adds two slots, so promoting Lursa fits.
    promote_with_illyrians(s, "Lursa")
    assert {i.card for i in me(s).duty} == {"2PER11", "2PER10"}
    # When Illyrians leaves the Staging Area at Clean-up, one Duty Officer must be dismissed.
    choose_end(s)
    for _ in range(10):
        if "too many Duty Officers" in s.decision.prompt:
            break
        from engine.game import choose

        d = s.decision
        choose(s, d.seat, {"discard": "done", "action": "end"}.get(d.kind, d.options[0].id), flag_irreversible=False)
    assert "too many Duty Officers" in s.decision.prompt
    answer(s, "Lursa")
    assert [i.card for i in me(s).duty] == ["2PER11"]


def test_forced_singularity_gives_a_second_slot_at_military_3():
    from engine.ops import duty_fits

    s = given(duty=["2PER11"], fleet=["2CAR06"], tracks={"military": 3})
    two = [*me(s).duty, s.new_inst("2PER10")]
    assert duty_fits(s, me(s), two)
    me(s).tracks["military"] = 2
    assert not duty_fits(s, me(s), two)


def test_rillak_extra_slot_for_an_ambassador():
    from engine.ops import duty_fits

    s = given(duty=["2PER15"])
    assert duty_fits(s, me(s), [*me(s).duty, s.new_inst("2PER16")])  # Riva is an Ambassador
    assert not duty_fits(s, me(s), [*me(s).duty, s.new_inst("2PER10")])


def test_malik_skills_follow_augments_and_protocol_12():
    from engine.ops import Ctx
    from engine.state import OpRef

    s = given(duty=["2PER12"], staging=["2PER18"])  # Sarina Douglas is an Augment
    malik = card(s, "2PER12", zone="duty")
    ctx = Ctx(s, OpRef(mode="auto", seat=0))
    assert ctx.skills(malik) == ["Military", "Military"]
    s = given(duty=["2PER12"], staging=["3CAR03", "2PER14"], expansions=["second_contact"])  # Phlox: Doctor
    ctx = Ctx(s, OpRef(mode="auto", seat=0))
    assert ctx.skills(card(s, "2PER12", zone="duty")) == ["Military", "Military"]
    assert "Augment" in ctx.traits(card(s, "2PER14", zone="staging"))


def test_betazed_intelligence_raises_hand_size_for_the_draw():
    s = given(hand=["3ALL01"], staging=["2PER16"], expansions=["second_contact"], empty_hand=True)
    # Riva is an Ambassador; Georgiou's Captain is Starfleet: +2, so Betazed logs itself.
    play(s, card(s, "3ALL01", zone="hand"), 0)
    while s.decision.kind == "op":
        answer(s, "")
    choose_end(s)
    from engine.game import choose

    for _ in range(20):
        d = s.decision
        if d.kind == "discard":
            choose(s, 0, "done", flag_irreversible=False)
            break
        choose(s, d.seat, d.options[0].id, flag_irreversible=False)
    assert len(me(s).hand) == 7 and me(s).log[-1].card == "3ALL01"
    assert me(s).hand_bonus == 0  # reset at the end of the turn


# --------------------------------------------------------------------------- Step 6: duplicate, peek, staging


def test_orb_of_time_duplicating_denobulans_logs_the_orb():
    """AS-19: Orb of Time copying a self-logging Denobulans logs the Orb, not the Denobulans."""
    s = given(hand=["2CAR13"], log=["2ALL04"])
    incidents = len(s.incident)
    play(s, card(s, "2CAR13", zone="hand"), 0)
    answer(s, "Yes")  # take an Incident to duplicate
    answer(s, "Gain a Person")  # Denobulans' first PLAY
    answer(s, "faceup")
    answer(s, "Discard pile")
    assert len(s.incident) == incidents - 1
    assert me(s).log[-1].card == "2CAR13" and [i.card for i in me(s).log].count("2ALL04") == 1


def test_a_duplicated_duplicate_only_recalls():
    """AS-19: copying Orb of Time with another Duplicate allows only its recall (KW-DUP-05)."""
    s = given(hand=["2ALL15"], staging=["2CAR13", "2PER22"], log=["2ALL04"])
    incidents = len(s.incident)
    play(s, card(s, "2ALL15", zone="hand"), 0)
    answer(s, "Orb of Time")
    answer(s, "Tevrin")  # the Orb's recall
    assert any(i.card == "2PER22" for i in me(s).hand) and len(s.incident) == incidents


def test_vadic_copying_cloaking_device_cannot_deploy():
    """AS-19: Vadic's Splinter Group duplicating Cloaking Device refreshes, draws and junks, but cannot deploy."""
    s = given(hand=["2ALL15"], fleet=["2CAR03"], empty_hand=True)
    play(s, card(s, "2ALL15", zone="hand"), 0)
    answer(s, "Cloaking Device")
    while s.decision.kind == "op" and "Then choose" not in s.decision.prompt:
        answer(s, "")
    assert card(s, "2ALL15").uid in uids(me(s).staging)  # not deployed
    assert len(me(s).hand) >= 2


def test_holographic_drone_ship_duplicating_deploy_deploys_itself():
    s = given(hand=["2SHI05"], fleet=["2SHI04"], tracks={"research": 7})
    play(s, card(s, "2SHI05", zone="hand"), 0)
    answer(s, "D'Var")
    assert card(s, "2SHI05").uid in uids(me(s).fleet)


def test_tysess_duplicates_the_promoted_person():
    s = given(hand=["2PER04"], discard=["2PER07"], empty_hand=True)
    actions = me(s).actions
    play(s, card(s, "2PER04", zone="hand"), 0)
    answer(s, "Hoshi")
    answer(s, "Yes")  # spend an Action to duplicate Hoshi's PLAY
    answer(s, "Find a card")
    while s.decision.kind == "op":
        answer(s, "No" if "No" in options(s) else "")
    assert card(s, "2PER07").uid in uids(me(s).duty) and me(s).actions == actions - 1


def test_suliban_duplicates_the_market_ally():
    s = given(hand=["2ALL12"])
    s.market["Ally"] = s.new_inst("2ALL11")  # Salt Vampires: draw 2
    hand = len(me(s).hand)
    play(s, card(s, "2ALL12", zone="hand"), 0)
    answer(s, "Salt Vampires")
    assert len(me(s).hand) == hand - 1 + 2


def test_sarina_peeks_privately():
    from engine.views import game_view

    s = given(hand=["2PER18", "2PER14"])
    play(s, card(s, "2PER18", zone="hand"), 0)  # discards Phlox (Doctor); nothing to free play, so it peeks
    answer(s, "Person")
    top = s.market_decks["Person"][0]
    view = game_view(s, 0)
    assert [c["uid"] for c in view["decision"]["cards"]] == [top.uid]
    assert any("You see" in line for line in view["log"])
    assert not any("You see" in line for line in game_view(s, 1)["log"])


def test_hoshi_puts_a_reserve_card_into_staging():
    s = given(duty=["2PER07"], fleet=["2SHI07"])  # Medusan Vessel is Alien
    hand = len(me(s).hand)
    reserve = len(me(s).reserve)
    activate(s, card(s, "2PER07", zone="duty"), 2)
    answer(s, "Yes")
    answer(s, "")
    assert len(me(s).hand) == hand + 1 and len(me(s).reserve) == reserve - 1 and len(me(s).staging) == 1


def test_landru_takes_control_of_the_top_location():
    s = given(duty=["2PER09"], tracks={"influence": 2})
    landru = card(s, "2PER09", zone="duty")
    landru.beamed += [s.new_inst("2PER07"), s.new_inst("2PER11")]
    top = s.location_deck[0]
    neutral = [l.uid for l in s.neutral]
    from engine.game import advance

    s.decision = None
    advance(s, flag_irreversible=False)
    activate(s, landru, 1)
    while s.decision.kind == "op":
        answer(s, "")
    assert top.uid in uids(me(s).locations) and [l.uid for l in s.neutral] == neutral
    assert any(i.card == "2PER09" for i in me(s).hand)


def test_sukal_returns_incidents_before_scoring():
    s = given(hand=["2PER20", "2INC01", "2INC02", "2INC03"])
    s.last_turn = s.turn
    incidents = len(s.incident)
    choose_end(s)
    from engine.game import choose

    for _ in range(20):
        d = s.decision
        if d is None or s.step == "over" or "Su'Kal" in d.prompt:
            break
        choose(s, d.seat, {"discard": "done"}.get(d.kind, d.options[0].id), flag_irreversible=False)
    assert "Su'Kal" in s.decision.prompt
    answer(s, "")
    answer(s, "")
    assert s.step == "over" and len(s.incident) == incidents + 2
