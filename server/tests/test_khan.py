"""Khan's Crew deck, Crew board and missions (plans/card-implementation.md Step 18; requirements/15-crew-decks.md §4)."""

import random

import pytest

from engine import cards as registry
from engine.content import content
from engine.game import HANDLERS, _advance_untracked, advance, choose
from engine.ops import A, Actions, Ctx, UndeclaredActionError, _payable_developments, mark_options, rival_pairs
from engine.scoring import score_player
from engine.setup import SeatSetup, new_game
from engine.state import Mark, OpRef
from engine.views import game_view
from tests.scenario import activate, answer, can_play, card, given, options, play
from tests.test_market_cards import RICH, finish

CARDS = content().cards
KHAN = sorted(c for c in CARDS if c.startswith("2KHA"))
BOARD = content().boards["cb-khan"]


def me(s):
    return s.players[0]


def opp(s):
    return s.players[1]


def uids(cards):
    return [i.uid for i in cards]


def refresh(s):
    s.decision = None
    advance(s, flag_irreversible=False)


def khan(**kw):
    kw.setdefault("opponent", "soval")
    return given(deck="khan", board="advanced", **kw)


def ctx_of(s, seat=0, uid=None):
    return Ctx(s, OpRef(mode="auto", seat=seat, uid=uid))


def run(gen):
    """Drive an action that asks nothing to its end and return its result."""
    try:
        next(gen)
    except StopIteration as stop:
        return stop.value
    raise AssertionError("the action asked a question")


def queue(s, inst, index, mode="auto", event=None):
    s.op_queue.append(OpRef(mode=mode, seat=0, uid=inst.uid, index=index, event=event))
    refresh(s)


def zone_for(cid):
    return {"Person": "duty", "Location": "locations"}.get(CARDS[cid].suit, "fleet")


# --------------------------------------------------------------------------- setup and the deck's own rules


def test_setup_hand_six_no_reserve_and_an_unmarked_board():
    s = new_game(3, "two_player", [SeatSetup("K", "khan", "advanced"), SeatSetup("S", "soval", "basic")])
    assert len(me(s).hand) == 6 and not me(s).reserve and not me(s).marks  # REQ-CD-KHN-02, -03, -06
    assert me(s).captain.card == "2KHA01A" and {i.card for i in me(s).locations} == {"2KHA02A", "2KHA03"}
    assert all(not i.card.endswith("B") for i in me(s).draw + me(s).hand + me(s).development)  # hidden sides (REQ-CD-KHN-01)
    assert len(BOARD.trait_order) == BOARD.trait_slots == 12


def test_board_order_is_alphabetical_then_the_opponent_entries():
    assert BOARD.trait_order == ("ambassador", "business", "cloak", "creature", "doctor", "engineer", "scientist",
                                 "spy", "synthetic", "telepath", "captain-trait", "different-trait-than-opponent")


def test_every_khan_card_and_mission_has_code():
    for cid in KHAN:
        for index, op in enumerate(CARDS[cid].operations):
            if op.kind != "SURPRISE":  # the four SURPRISE operations wait for the Khan Bot
                assert registry.has_code(cid, index, op.kind), (cid, index, op.kind)
    for (cid, index), impl in registry.OPS.items():
        if cid.startswith("2KHA"):  # the code declares exactly the actions its spec lists
            assert set(impl.uses) == set(CARDS[cid].operations[index].uses), (cid, index)
    for mission in BOARD.missions:
        impl = registry.MISSIONS[mission.id]
        assert impl.goal and impl.reward and set(impl.uses) == set(mission.uses)


def test_no_enlisting_on_a_cycle_and_ceti_alpha_vi_fills():
    s = khan(hand=["2KHA06"], empty_hand=True)
    me(s).discard.extend(me(s).draw)
    me(s).draw.clear()
    developments = len(me(s).development)
    play(s, card(s, "2KHA06", zone="hand"), 0)  # Cpt. Terrell draws 2: the deck cycles
    while s.decision.kind == "op":
        answer(s, "")
    vi = card(s, "2KHA03", zone="locations")
    assert len(me(s).development) == developments and vi.res.get("dilithium") == 2  # REQ-CD-KHN-03; the PASSIVE


def test_gaining_specialty_does_nothing_and_requirements_fail_until_wrathful():
    s = khan()
    acts = Actions(ctx_of(s), (A.GAIN_SPECIALTY,))
    run(acts.gain_specialty("military", 3))
    assert me(s).tracks["military"] == 0 and ctx_of(s).track("military") == 0  # REQ-CD-KHN-04
    me(s).captain.card = "2KHA01B"
    assert ctx_of(s).track("military") == 15 and ctx_of(s).track("research") == 15
    assert ctx_of(s, seat=1).track("military") == 0  # only Khan ignores them


def test_focus_icons_score_only_when_wrathful():
    s = khan(discard=["2ALL06", "2ALL07"])  # two cards with a Focus icon
    me(s).missions_completed.append("ive-hurt-you")
    parts = score_player(s, me(s))["parts"]
    assert parts["endgame"] == 0 and parts["focus_research"] + parts["focus_influence"] + parts["focus_military"] == 0
    me(s).captain.card = "2KHA01B"
    assert score_player(s, me(s))["parts"]["endgame"] == 2  # 1 VP each (REQ-CD-KHN-05)
    me(s).marks = [Mark(slot=slot, trait=slot) for slot in BOARD.trait_order]
    assert score_player(s, me(s))["parts"]["endgame"] == 6  # 3 VP each with all 12 marked


# --------------------------------------------------------------------------- marking traits (REQ-CD-KHN-06 to -09)


def test_gaining_a_card_offers_one_mark():
    s = khan(hand=["2KHA15"], latinum=1)
    s.junk.append(s.new_inst("2PER13"))  # Petra Aberdeen: Human, Scientist
    play(s, card(s, "2KHA15", zone="hand"), 1)  # Salvage: gain from the Junk
    while "Mark a trait" not in s.decision.prompt:
        answer(s, "")
    assert options(s) == ["Scientist", "Do not mark a trait"]
    answer(s, "Scientist")
    assert [(m.slot, m.trait) for m in me(s).marks] == [("scientist", "Scientist")]


def test_a_marked_trait_is_not_offered_again_and_marking_is_optional():
    s = khan(hand=["2KHA15", "2KHA15"], latinum=2)
    s.junk += [s.new_inst("2PER13"), s.new_inst("2PER05")]  # two Scientists
    play(s, card(s, "2KHA15", zone="hand"), 1)
    while "Mark a trait" not in s.decision.prompt:
        answer(s, "")
    answer(s, "Scientist")
    play(s, card(s, "2KHA15", zone="hand"), 1)
    while s.decision.kind == "op":
        assert "Mark a trait" not in s.decision.prompt
        answer(s, "")
    assert len(me(s).marks) == 1


def test_taking_a_card_does_not_allow_marking():
    s = khan(marks=6)
    choose(s, 0, "mission:ive-hurt-you", flag_irreversible=False)  # the reward takes an Encounter
    assert s.decision.kind == "action" and len(me(s).marks) == 6  # REQ-CD-KHN-07
    assert any(CARDS[i.card].suit == "Encounter" for i in me(s).hand)


def test_taking_control_marks_before_the_control_operation():
    from engine.game import take_control

    s = khan()
    risa = s.new_inst("2LOC09")  # Business
    s.neutral.append(risa)
    take_control(s, me(s), risa)
    refresh(s)
    assert "Mark a trait for Risa" in s.decision.prompt  # asked first (REQ-CD-KHN-08)
    answer(s, "Business")
    assert me(s).marks[0].slot == "business" and risa.uid in uids(me(s).locations)


def test_a_card_can_mark_only_its_own_unmarked_traits():
    s = khan(opponent="kirk")
    vampires = s.new_inst("2ALL11")  # Telepath, Creature
    s.junk.append(vampires)
    assert mark_options(s, me(s), vampires) == [("creature", "Creature"), ("telepath", "Telepath")]
    me(s).marks.append(Mark(slot="creature", trait="Creature"))
    assert mark_options(s, me(s), vampires) == [("telepath", "Telepath")]


def _entries(s, card_id):
    inst = s.new_inst(card_id)
    s.junk.append(inst)
    return inst, [t for slot, t in mark_options(s, me(s), inst) if slot in ("captain-trait", "different-trait-than-opponent")]


def test_opponent_entries_against_soval_need_vulcan_and_one_board_trait():
    s = khan(opponent="soval")
    assert set(rival_pairs(s, me(s))) == {frozenset(("Vulcan", "Ambassador")), frozenset(("Vulcan", "Telepath"))}
    gral, traits = _entries(s, "2PER02")  # Ambassador
    assert traits == ["Ambassador"]
    me(s).marks.append(Mark(slot="captain-trait", trait="Ambassador", card=gral.uid))
    assert _entries(s, "2ALL07")[1] == []  # Telepath cannot fill the other: one entry must be Vulcan
    assert _entries(s, "2SHI03")[1] == ["Vulcan"]


def test_opponent_entries_against_kirk_are_starfleet_and_human():
    s = khan(opponent="kirk")
    assert rival_pairs(s, me(s)) == [frozenset(("Human", "Starfleet"))]
    assert _entries(s, "2PER13")[1] == ["Human"]  # Petra Aberdeen: Human, Scientist


def test_opponent_entries_against_archer_exclude_human():
    s = khan(opponent="archer")
    pairs = rival_pairs(s, me(s))
    assert len(pairs) == 3 and all("Human" not in pr for pr in pairs)
    assert _entries(s, "2PER13")[1] == []  # Human is not allowed while two other traits exist


def test_khan_against_khan_uses_augment_and_human():
    s = khan(opponent="khan")
    assert rival_pairs(s, me(s)) == [frozenset(("Human", "Augment"))]


def test_the_same_card_cannot_mark_both_opponent_entries():
    s = khan(opponent="archer")
    hoshi, traits = _entries(s, "2PER07")  # NX-01, Human, Starfleet, Communication
    assert traits == ["NX-01", "Starfleet"]
    me(s).marks.append(Mark(slot="captain-trait", trait="NX-01", card=hoshi.uid))
    assert [t for _, t in mark_options(s, me(s), hoshi)] == []  # the same physical card
    assert _entries(s, "2PER07")[1] == ["Starfleet"]  # another copy can; and a different trait is needed


def test_a_wildcard_can_mark_any_slot_under_the_board_rule():
    s = khan(opponent="archer")
    koala = s.new_inst("2ENC04")  # Wildcard
    s.junk.append(koala)
    found = mark_options(s, me(s), koala, wildcard=True)
    assert len([slot for slot, _ in found if slot not in ("captain-trait",)]) == 10
    assert [t for slot, t in found if slot == "captain-trait"] == ["NX-01", "Pilot", "Starfleet"]
    assert mark_options(s, me(s), koala) == []  # "mark one trait of a card" effects read its own traits only


def test_the_view_lists_the_trait_tokens():
    s = khan(opponent="kirk", marks=1)
    traits = game_view(s, 0)["players"][0]["traits"]
    assert len(traits) == 12 and traits[0] == {"slot": "ambassador", "label": "Ambassador", "marked": True,
                                               "trait": "Ambassador", "image": "khan-ambassador-marked"}
    assert traits[1]["image"] == "khan-business" and not traits[1]["marked"]
    assert traits[10]["label"] == "Opponent's Captain: Human / Starfleet"
    assert game_view(s, 0)["players"][1]["traits"] is None


def test_mark_trait_must_be_declared():
    s = khan()
    with pytest.raises(UndeclaredActionError):
        run(Actions(ctx_of(s), ()).mark_trait())
    with pytest.raises(UndeclaredActionError):
        run(Actions(ctx_of(s), ()).flip(me(s).captain))


# --------------------------------------------------------------------------- missions


def test_missions_need_six_nine_and_twelve_marks():
    for marks, offered in ((5, set()), (6, {"ive-hurt-you"}), (9, {"ive-hurt-you", "i-shall-leave-you-as-you-left-me"}),
                           (12, {m.id for m in BOARD.missions})):
        s = khan(marks=marks)
        assert {o.id.split(":")[1] for o in s.decision.options if o.id.startswith("mission:")} == offered


def test_the_second_mission_is_the_only_thing_that_flips_the_captain():
    s = khan(marks=9)
    teams = me(s).away_pool
    choose(s, 0, "mission:i-shall-leave-you-as-you-left-me", flag_irreversible=False)
    while s.decision.kind == "op":
        answer(s, "")
    assert me(s).captain.card == "2KHA01B" and me(s).away_pool == teams  # Away Teams carry over (REQ-CD-KHN-01)
    assert any(CARDS[i.card].suit == "Encounter" for i in me(s).hand)
    assert registry.ENDGAME["2KHA01B"](s, me(s)) >= 0 and ctx_of(s).track("influence") == 15


def test_the_third_mission_makes_the_opponent_recall_and_log_a_person():
    s = khan(marks=12, opp={"duty": ["2PER11"]})
    choose(s, 0, "mission:marooned-for-all-eternity", flag_irreversible=False)
    while s.decision.kind == "op":
        answer(s, "")
    assert [i.card for i in opp(s).log] == ["2PER11"] and not opp(s).duty


def test_ceti_alpha_vi_flips_the_planet_but_not_the_captain():
    s = khan()
    vi = card(s, "2KHA03", zone="locations")
    vi.res["dilithium"] = 4
    s.neutral[0].away[0] = 2  # Away Teams already at a Location are sent home too
    me(s).away_pool -= 2
    dilithium, incidents = me(s).dilithium, len(opp(s).hand)
    queue(s, vi, 0)  # its RESUPPLY
    while s.decision.kind == "op":
        answer(s, "")
    home = next(i for i in me(s).locations if i.card == "2KHA02B")
    assert me(s).captain.card == "2KHA01A"  # ruling: only the mission flips Khan
    assert me(s).dilithium == dilithium + 4 and vi.uid in uids(me(s).log)
    assert len(opp(s).hand) == incidents + 1 and home.away.get(0) == 4 and me(s).away_pool == 0 and 0 not in s.neutral[0].away
    from engine.game import hand_size

    assert hand_size(s, me(s)) == 5  # Ceti Alpha V no longer raises it (REQ-CD-KHN-02)


def test_ceti_alpha_vi_resupply_waits_for_four_dilithium():
    s = khan()
    vi = card(s, "2KHA03", zone="locations")
    vi.res["dilithium"] = 3
    queue(s, vi, 0)
    assert vi.uid in uids(me(s).locations) and vi.res["dilithium"] == 3


# --------------------------------------------------------------------------- the Captain


def test_the_normal_side_passive_is_mandatory():
    s = khan(hand=["2PER13"], empty_hand=True)
    s.pending_events.append({"kind": "return_incident", "seat": 1, "uid": None})
    refresh(s)
    assert s.decision.kind == "op" and "Gain which resource" in s.decision.prompt  # the only card was discarded
    answer(s, "Latinum")
    assert me(s).latinum == 2 and not me(s).hand and not me(s).captain.exhausted  # no exhaust: it can trigger again


def test_the_normal_side_passive_does_nothing_with_an_empty_hand():
    s = khan(empty_hand=True)
    s.pending_events.append({"kind": "return_incident", "seat": 1, "uid": None})
    refresh(s)
    assert s.decision.kind == "action" and me(s).dilithium == 1


def test_your_own_returned_incident_does_not_trigger_it():
    s = khan()
    hand = len(me(s).hand)
    s.pending_events.append({"kind": "return_incident", "seat": 0, "uid": None})
    refresh(s)
    assert s.decision.kind == "action" and len(me(s).hand) == hand


def test_the_wrathful_side_reaction_is_optional_and_exhausts():
    s = khan()
    me(s).captain.card = "2KHA01B"
    s.pending_events.append({"kind": "return_incident", "seat": 1, "uid": None})
    refresh(s)
    assert s.decision.kind == "trigger" and "Do not use" in options(s)
    answer(s, "Wrathful Khan")
    while s.decision.kind == "op":
        answer(s, "Dilithium" if "Dilithium" in " ".join(options(s)) else "")
    assert me(s).dilithium == 2 and me(s).captain.exhausted


def test_the_captain_activation_needs_an_incident():
    s = khan(empty_hand=True)
    captain = me(s).captain
    assert f"activate:{captain.uid}:0" not in {o.id for o in s.decision.options}
    s = khan(hand=["2INC01"], empty_hand=True)
    captain = me(s).captain
    activate(s, captain, 0)
    while s.decision.kind == "op":
        answer(s, "")
    assert len(me(s).hand) == 1 and any(i.card == "2INC01" for i in me(s).discard)


# --------------------------------------------------------------------------- every operation runs


NEEDS_OWN_SETUP = {
    ("2KHA03", 2): "needs Dilithium on the card and a secured Location",
    ("2KHA14", 2): "needs a Ship at the Mutara Nebula",
    ("2KHA16", 3): "needs 3 Persons beamed to the Botany Bay",
}


@pytest.mark.parametrize("cid,index", [(cid, i) for cid in KHAN for i, op in enumerate(CARDS[cid].operations)
                                       if op.kind in ("PLAY", "ACTIVATION") and not cid.endswith("B")])
def test_every_khan_operation_runs(cid, index):
    if (cid, index) in NEEDS_OWN_SETUP:
        pytest.skip(NEEDS_OWN_SETUP[(cid, index)])
    kind = CARDS[cid].operations[index].kind
    position = {**RICH, "hand": RICH["hand"] + ["2KHA17"], "opp": {"duty": ["2PER04"]}}
    if CARDS[cid].suit == "Captain" or cid in ("2KHA03",):
        pass  # already in play
    elif kind == "PLAY":
        position["hand"] = position["hand"] + [cid]
    else:
        z = zone_for(cid)
        position[z] = [cid] if z == "duty" else RICH.get(z, []) + [cid]
    for seed in range(2):
        s = khan(**position)
        for ship in me(s).fleet:
            if ship.card != "2KHA16":
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


def test_ceti_alpha_vi_takes_control_of_a_secured_location():
    s = khan(latinum=1)
    vi = card(s, "2KHA03", zone="locations")
    assert f"activate:{vi.uid}:2" not in {o.id for o in s.decision.options}  # no Dilithium here, nothing secured
    vi.res["dilithium"] = 2
    target = s.neutral[0]
    target.away[0] = 3
    refresh(s)
    incidents = len(s.incident)
    activate(s, vi, 2)
    while s.decision.kind == "op":
        answer(s, "Do not" if "Do not mark a trait" in options(s) else "")
    assert target.uid in uids(me(s).locations) and vi.res["dilithium"] == 1 and len(s.incident) == incidents - 1


def test_devastated_ceti_alpha_v_operations():
    s = khan(hand=["2KHA17"], empty_hand=True)
    home = card(s, "2KHA02A", zone="locations")
    home.card = "2KHA02B"
    refresh(s)
    activate(s, home, 1)  # no Away Team here: draw a card
    assert len(me(s).hand) == 2 and home.exhausted
    s.pending_events.append({"kind": "return_incident", "seat": 0, "uid": None})
    refresh(s)
    assert not home.exhausted  # PASSIVE: after returning an Incident, refresh this card
    play(s, card(s, "2KHA17", zone="hand"), 0)  # Wajahut is an Augment
    while s.decision.kind == "op":
        answer(s, "")
    assert s.decision.kind == "trigger" and "Devastated Ceti Alpha V" in options(s)[0]
    hand = len(me(s).hand)
    answer(s, "Devastated")
    while s.decision.kind == "op":
        answer(s, "No")
    assert len(me(s).hand) == hand + 1


def test_hijacked_reliant_needs_a_mind_control_person():
    s = khan(dilithium=5)
    assert "2KHA04" not in [i.card for i in _payable_developments(ctx_of(s))]
    s = khan(dilithium=5, duty=["2KHA06"])  # Cpt. Terrell
    assert "2KHA04" in [i.card for i in _payable_developments(ctx_of(s))]


def test_cpt_terrell_enlists_without_resources_but_keeps_the_conditions():
    s = khan(hand=["2KHA06"], dilithium=-1, latinum=-1, glory=-1)
    assert (me(s).dilithium, me(s).latinum, me(s).glory) == (0, 0, 0)
    play(s, card(s, "2KHA06", zone="hand"), 1)
    names = " ".join(options(s))
    assert "Hijacked U.S.S. Reliant" in names  # Terrell himself is the Mind Control Person in play
    assert "Revenge" not in names and "Genesis Device" not in names  # their conditions still apply
    incidents = len(s.incident)
    answer(s, "Surprise Attack")  # normally 2 Dilithium and an Incident
    assert me(s).draw[0].card == "2KHA05" and len(s.incident) == incidents and me(s).log[-1].card == "2KHA06"


def test_ceti_eel_dismisses_a_duty_officer_and_returns_to_the_development_pile():
    s = khan(hand=["2KHA08"])
    assert not can_play(s, card(s, "2KHA08", zone="hand"), 0)  # no opponent Duty Officer
    s = khan(hand=["2KHA08"], opp={"duty": ["2PER11"]})
    s.neutral[0].away[1] = 1  # only this neutral Location has a token
    eel = card(s, "2KHA08", zone="hand")
    play(s, eel, 0)
    while s.decision.kind == "op":
        answer(s, "No")
    assert not opp(s).duty and s.neutral[0].away[0] == 2 and eel.uid in uids(me(s).development)


def test_ceti_eel_finds_and_logs():
    s = khan(hand=["2KHA08", "2INC01"], empty_hand=True)
    eel = card(s, "2KHA08", zone="hand")
    play(s, eel, 1)
    target = next(o.label for o in s.decision.options if "Marla McGivers" in o.label)
    answer(s, target)
    answer(s, "Dilithium Shockwave")  # return the Incident
    assert {i.card for i in me(s).log} == {"2KHA13", "2KHA08"} and not me(s).hand


def test_revenge_needs_marla_logged_and_marks_from_the_opponents_discard():
    s = khan(latinum=5)
    assert "2KHA10" not in [i.card for i in _payable_developments(ctx_of(s))]
    s = khan(latinum=5, log=["2KHA13"], hand=["2KHA10"], opp={"discard": ["2PER13"]})
    assert "2KHA10" in [i.card for i in _payable_developments(ctx_of(s))]
    glory = me(s).glory
    play(s, card(s, "2KHA10", zone="hand"), 0)
    assert s.decision.seat == 1 and "Find any card" in s.decision.prompt
    logged = s.decision.options[0].id.split(":")[1]
    choose(s, 1, s.decision.options[0].id, flag_irreversible=False)
    answer(s, "Petra Aberdeen")
    assert me(s).glory == glory + 1 and logged in uids(opp(s).log)
    assert [(m.slot, m.trait) for m in me(s).marks] == [("scientist", "Scientist")]


def test_revenge_goes_to_the_opponents_log_and_costs_them_per_incident():
    s = khan(hand=["2KHA10", "2KHA17", "2INC01"], empty_hand=True)
    revenge = card(s, "2KHA10", zone="hand")
    play(s, revenge, 1)  # discards Wajahut, the only Augment
    answer(s, "Dilithium Shockwave")
    while s.decision.kind != "action":
        answer(s, "Do not use" if "Do not use" in options(s) else "")
    them = opp(s)
    assert {i.card for i in them.log} == {"2KHA10", "2INC01"}
    assert registry.VP_SPECIAL["2KHA10"](s, them, revenge) == -1  # each of their Incidents scores 1 VP less
    assert not can_play(s, revenge, 1)


def test_revenge_in_cadet_training():
    s = given(deck="khan", board="advanced", mode="cadet", hand=["2KHA10", "2KHA17", "2INC01"], empty_hand=True)
    glory = me(s).glory
    play(s, card(s, "2KHA10", zone="hand"), 1)
    answer(s, "Dilithium Shockwave")
    owned = {i.card for z in (me(s).hand, me(s).discard, me(s).log, me(s).staging) for i in z}
    assert me(s).glory == glory + 4 and not owned & {"2KHA10", "2INC01"}  # both destroyed (REQ-CD-KHN-10)


def test_revenge_marks_from_the_junk_in_cadet_training():
    s = given(deck="khan", board="advanced", mode="cadet", hand=["2KHA10"])
    s.junk.append(s.new_inst("2PER13"))
    play(s, card(s, "2KHA10", zone="hand"), 0)
    assert "the Junk" in s.decision.prompt
    answer(s, "Petra Aberdeen")
    assert me(s).marks[0].trait == "Scientist"


def test_genesis_device_marks_destroys_and_scores_missions_again():
    s = khan(hand=["2KHA11"], opponent="kirk")
    doomed = s.neutral[0]
    doomed.away[1] = 2
    pool, glory, zone = opp(s).away_pool, opp(s).glory, len(s.neutral)
    device = card(s, "2KHA11", zone="hand")
    play(s, device, 0)
    assert len(options(s)) == 12  # any one trait: ten printed ones, and Human or Starfleet for a Captain entry
    answer(s, "Telepath")
    answer(s, CARDS[doomed.card].name)
    while s.decision.kind != "action":
        answer(s, "")
    assert me(s).marks[0].slot == "telepath" and device.uid in uids(me(s).fleet)
    assert doomed.uid not in uids(s.neutral) and len(s.neutral) == zone  # destroyed, and the Neutral Zone refilled
    assert opp(s).away_pool == pool + 2 and opp(s).glory == glory  # no Glory compensation
    me(s).missions_completed += ["ive-hurt-you", "i-shall-leave-you-as-you-left-me"]
    assert registry.ENDGAME["2KHA11"](s, me(s)) == 3


def test_genesis_device_needs_an_empty_development_pile():
    s = khan(dilithium=5, latinum=5)
    assert "2KHA11" not in [i.card for i in _payable_developments(ctx_of(s))]
    me(s).development = [i for i in me(s).development if i.card == "2KHA11"]
    assert "2KHA11" in [i.card for i in _payable_developments(ctx_of(s))]


def test_vacated_regula_i():
    s = khan(hand=["2KHA12"])
    assert not can_play(s, card(s, "2KHA12", zone="hand"), 0)  # no Ship at a neutral Location
    s = khan(hand=["2KHA12"], fleet=["2SHI03"], opponent="kirk")
    card(s, "2SHI03", zone="fleet").at = s.neutral[0].uid
    s.junk.append(s.new_inst("2PER05"))  # Degra: Scientist
    refresh(s)
    station = card(s, "2KHA12", zone="hand")
    play(s, station, 0)
    assert "Mark a trait for Vacated Regula I" in s.decision.prompt  # Starfleet matches Kirk's Captain
    answer(s, "Starfleet")
    answer(s, "Yes")  # CONTROL: take an Incident to mark a trait of a card in the Junk
    while s.decision.kind == "op":
        answer(s, "")
    assert [m.trait for m in me(s).marks] == ["Starfleet", "Scientist"] and station.uid in uids(me(s).locations)
    assert any(CARDS[i.card].suit == "Incident" for i in me(s).hand)
    glory, pile = me(s).glory, len(me(s).development)
    activate(s, station, 3)
    while s.decision.kind == "op":
        answer(s, "")
    assert me(s).glory == glory + 1 and len(me(s).development) == pile - 1


def test_regula_i_returns_an_incident_after_a_scientist():
    s = khan(locations=["2KHA12"], hand=["2PER13"], discard=["2INC01"])
    play(s, card(s, "2PER13", zone="hand"), 0)
    while s.decision.kind == "op":
        answer(s, "")
    assert s.decision.kind == "trigger" and "Vacated Regula I" in options(s)[0]
    answer(s, "Vacated Regula I")
    assert not any(i.card == "2INC01" for i in me(s).discard)


def test_marla_mcgivers_clean_up_enlists_the_eel_and_logs_her():
    s = khan(duty=["2KHA13"])
    home = card(s, "2KHA02A", zone="locations")
    home.card = "2KHA02B"
    home.exhausted = True
    marla = card(s, "2KHA13", zone="duty")
    queue(s, marla, 1)
    assert me(s).draw[0].card == "2KHA08" and marla.uid in uids(me(s).log)


def test_marla_mcgivers_stays_while_the_planet_is_ready():
    s = khan(duty=["2KHA13"])
    marla = card(s, "2KHA13", zone="duty")
    queue(s, marla, 1)
    assert marla.uid in uids(me(s).duty)


def test_marla_mcgivers_play_counts_starfleet_and_locations():
    s = khan(hand=["2KHA13"], empty_hand=True)
    dilithium = me(s).dilithium
    play(s, card(s, "2KHA13", zone="hand"), 0)
    assert me(s).dilithium == dilithium + 3  # Marla herself is Starfleet, plus the two Ceti Alpha Locations


def test_mutara_nebula_depends_on_seven_marks():
    s = khan(hand=["2KHA14", "2PER13", "2PER05"], empty_hand=True)
    nebula = card(s, "2KHA14", zone="hand")
    play(s, nebula, 0)
    while s.decision.kind == "op":
        answer(s, "")
    assert not me(s).hand and nebula.uid in uids(me(s).locations)  # fewer than 7: discard 2 cards
    s = khan(hand=["2KHA14"], empty_hand=True, marks=7)
    s.junk.append(s.new_inst("2SHI03"))
    play(s, card(s, "2KHA14", zone="hand"), 0)
    while s.decision.kind == "op":
        answer(s, "Do not" if "Do not mark a trait" in options(s) else "")
    assert any(i.card == "2SHI03" for i in me(s).draw + me(s).discard)


def test_mutara_nebula_warps_a_ship_and_sends_a_team():
    s = khan(locations=["2KHA14"], fleet=["2SHI03"], dilithium=1)
    nebula = card(s, "2KHA14", zone="locations")
    ship = card(s, "2SHI03", zone="fleet")
    assert f"activate:{nebula.uid}:2" not in {o.id for o in s.decision.options}  # no Ship here
    ship.at = nebula.uid
    refresh(s)
    activate(s, nebula, 2)
    target = s.neutral[0]
    answer(s, CARDS[target.card].name)
    assert card(s, "2SHI03", zone="fleet").at == target.uid and s.neutral[0].away[0] == 1


def test_the_botany_bay_cannot_be_warped():
    s = khan(fleet=["2KHA16"])
    bay = card(s, "2KHA16", zone="fleet")
    acts = Actions(ctx_of(s), (A.WARP,))
    assert not acts.can_warp(bay) and run(acts.warp(bay)) is None and bay.at is None


def test_the_botany_bay_takes_a_location_and_is_logged():
    s = khan(fleet=["2KHA16"])
    bay = card(s, "2KHA16", zone="fleet")
    assert f"activate:{bay.uid}:3" not in {o.id for o in s.decision.options}  # fewer than 3 Persons
    bay.beamed += [s.new_inst("2PER13"), s.new_inst("2PER05"), s.new_inst("2PER11")]
    refresh(s)
    first, second = s.location_deck[0], s.location_deck[1]
    activate(s, bay, 3)
    answer(s, CARDS[second.card].name)
    while s.decision.kind == "op":
        answer(s, "Do not" if "Do not mark a trait" in options(s) else "")
    assert second.uid in uids(me(s).locations) and s.location_deck[-1].uid == first.uid
    assert bay.uid in uids(me(s).log) and sum(1 for i in me(s).discard if CARDS[i.card].suit == "Person") >= 3


def test_wajahut_reaction_gains_an_action_or_enlists():
    s = khan(duty=["2KHA17"], dilithium=3, latinum=3)
    wajahut = card(s, "2KHA17", zone="duty")
    actions = me(s).actions
    queue(s, wajahut, 2, mode="trigger", event={"kind": "take_control", "seat": 0, "uid": None})
    while "which effect" not in s.decision.prompt:
        answer(s, "")
    answer(s, "Spend an Action")
    answer(s, "Infiltrate")
    assert me(s).actions == actions - 1 and me(s).draw[0].card == "2KHA09" and wajahut.uid in uids(me(s).discard)


def test_wajahut_and_joachim_together_gain_an_action():
    s = khan(hand=["2KHA17"], duty=["2KHA18"])
    actions = me(s).actions
    play(s, card(s, "2KHA17", zone="hand"), 1)
    while s.decision.kind == "op":
        answer(s, "")
    assert me(s).actions == actions  # one spent to play, one gained


def test_joachim_draws_with_a_weapon_or_security_in_play():
    s = khan(hand=["2KHA18"], duty=["2PER11"], empty_hand=True)  # Malcolm Reed: Security
    play(s, card(s, "2KHA18", zone="hand"), 1)
    while "Draw a card" not in s.decision.prompt:
        answer(s, "")
    answer(s, "Draw from your deck")
    answer(s, "Stop")
    assert len(me(s).hand) == 1


def test_khans_incidents_go_to_the_opponents_discard_pile():
    s = khan(opponent="archer", hand=["2KHA19", "2PER07"], empty_hand=True)  # Hoshi Sato shares NX-01 and Starfleet
    glory = me(s).glory
    curse = card(s, "2KHA19", zone="hand")
    assert registry.OPS[("2KHA19", 0)].fn is registry.OPS[("2KHA20", 0)].fn is registry.OPS[("2KHA21", 0)].fn
    play(s, curse, 0)
    while s.decision.kind == "op":
        answer(s, "No")
    assert curse.uid in uids(opp(s).discard) and me(s).draw[0].card == "2PER07" and me(s).glory == glory + 1


def test_khans_incidents_need_a_card_to_reveal():
    s = khan(hand=["2KHA20"], empty_hand=True)
    assert not can_play(s, card(s, "2KHA20", zone="hand"), 0)


def test_two_dimensional_thinking():
    s = khan(hand=["2KHA22"], discard=["2PER13"], empty_hand=True, opp={"fleet": ["2SHI03"]})
    thinking = card(s, "2KHA22", zone="hand")
    play(s, thinking, 0)
    answer(s, "Petra Aberdeen")  # draw a card from your Discard pile
    assert s.decision.seat == 1  # the opponent may warp a Ship
    answer(s, "D'Kyr Cruiser")
    while s.decision.kind == "op":
        answer(s, "")
    assert any(i.card == "2PER13" for i in me(s).hand) and thinking.uid in uids(s.incident)
    assert card(s, "2SHI03", seat=1, zone="fleet").at is not None


def test_surprise_attack_gives_an_incident():
    s = khan(hand=["2KHA05", "2INC01"], empty_hand=True, dilithium=1)
    play(s, card(s, "2KHA05", zone="hand"), 0)
    while s.decision.kind != "action":
        answer(s, "Do not use" if "Do not use" in options(s) else "")
    assert any(i.card == "2INC01" for i in opp(s).hand)
    s = khan(hand=["2KHA05", "2INC01"], empty_hand=True, dilithium=-1, glory=-1)
    assert not can_play(s, card(s, "2KHA05", zone="hand"), 0)  # cannot spend 1 Dilithium


def test_infiltrate_warps_only_cloaked_ships():
    s = khan(hand=["2KHA09"], fleet=["2SHI11", "2SHI03"])  # Vor'cha has Cloak, the D'Kyr does not
    play(s, card(s, "2KHA09", zone="hand"), 0)
    assert options(s) == ["Vor'cha Attack Cruiser", "Stop"]


# --------------------------------------------------------------------------- Cadet Training and random games


def test_cadet_training_picks_a_random_other_captain():
    s = new_game(5, "cadet", [SeatSetup("K", "khan", "advanced")])
    assert me(s).rival_captain is not None and CARDS[me(s).rival_captain].suit == "Captain"
    assert CARDS[me(s).rival_captain].deck != "khan" and rival_pairs(s, me(s))  # REQ-CD-KHN-10
    other = new_game(5, "cadet", [SeatSetup("K", "khan", "advanced")])
    assert other.players[0].rival_captain == me(s).rival_captain  # from the seed, so replay gives the same


def _play_out(s, rng, limit=1500):
    advance(s, flag_irreversible=False)
    for _ in range(limit):
        if s.step == "over":
            break
        d = s.decision
        ids = [o.id for o in d.options]
        plays = [i for i in ids if i.startswith(("play:", "activate:", "mission:"))]
        option = rng.choice(plays) if plays and rng.random() < 0.8 else rng.choice(ids)
        s.decision = None
        HANDLERS[d.kind](s, s.player(d.seat), option)
        _advance_untracked(s)
    for p in s.players:
        seen = [i.uid for z in ("hand", "draw", "discard", "reserve", "development", "staging", "fleet", "locations",
                                "duty", "log") for i in getattr(p, z)]
        assert len(seen) == len(set(seen)), "a card is in two places"
        assert len({m.slot for m in p.marks}) == len(p.marks) <= 12


@pytest.mark.parametrize("seed", range(16))
def test_random_games_with_khan(seed):
    rivals = ["soval", "kirk", "archer", "georgiou", "rebner", "khan", "pike", "riker"]
    rival = rivals[seed % len(rivals)]
    expansions = ["second_contact"] if rival in ("pike", "riker") or seed % 3 == 0 else []
    seats = [SeatSetup("K", "khan", "advanced"), SeatSetup("R", rival, "advanced" if seed % 2 else "basic")]
    s = new_game(seed, "two_player", seats if seed % 4 else seats[::-1], expansions)
    _play_out(s, random.Random(seed))


@pytest.mark.parametrize("seed", range(8))
def test_random_cadet_games_with_khan(seed):
    s = new_game(seed, "cadet", [SeatSetup("K", "khan", "advanced")], ["second_contact"] if seed % 2 else [])
    _play_out(s, random.Random(seed))
    assert s.step == "over"


@pytest.mark.parametrize("seed", range(6))
def test_random_solo_games_with_khan_against_a_bot(seed):
    from engine.setup import BotSetup

    bots = ["soval", "kirk", "archer", "georgiou", "rebner", "pike"]
    expansions = ["second_contact"] if bots[seed] == "pike" else []
    s = new_game(seed, "solo", [SeatSetup("K", "khan", "advanced")], expansions, bot=BotSetup(bots[seed], "ensign"))
    _play_out(s, random.Random(seed))
