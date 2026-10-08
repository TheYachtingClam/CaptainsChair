"""The Core Box common Market cards (plans/base-game.md Step 5): each spec's Tests cases, and the reprints and old
versions that share code. Specs: resources/scans/base_game/cards/{ally,cargo,person,ships}/."""

from engine import cards as registry
from engine.content import content
from tests.scenario import activate, answer, can_play, card, given, options, play
from tests.test_market_cards import finish

CARDS = content().cards


def me(s):
    return s.players[0]


def opp(s):
    return s.players[1]


def hand_ids(s, seat=0):
    return [i.card for i in s.players[seat].hand]


def can_activate(s, inst, index):
    return f"activate:{inst.uid}:{index}" in {o.id for o in s.decision.options}


# ------------------------------------------------------------------ reprints and old versions

def test_reprints_share_the_code_of_the_to_boldly_go_card():
    for c in CARDS.values():
        if c.same_as and c.is_common and CARDS[c.same_as].is_common:
            for index, op in enumerate(c.operations):
                if op.kind in ("PLAY", "ACTIVATION", "REACTION", "CONTROL", "RESUPPLY", "CLEAN-UP"):
                    assert registry.OPS[(c.id, index)].fn is registry.OPS[(c.same_as, index)].fn, (c.id, index)
    assert "1ENC03" in registry.HAND_SIZE and "1ENC03" in registry.SCANS_INCLUDE_JUNK  # Guardian of Forever
    assert "1PER22" in registry.BEFORE_SCORING  # Su'Kal
    assert "1LOC19" in registry.ENDGAME  # Verex III


def test_every_core_market_operation_has_code_and_declares_the_spec_actions():
    for c in CARDS.values():
        if c.set == "base_game" and c.is_common and c.suit in ("Ally", "Cargo", "Person", "Ship"):
            for index, op in enumerate(c.operations):
                assert registry.has_code(c.id, index, op.kind), (c.id, c.name, index)
                impl = registry.OPS.get((c.id, index))
                if impl is not None and not c.same_as and not c.replaced_by:
                    assert set(impl.uses) == set(op.uses), (c.id, c.name, index)


def test_riva_reprint_plays_like_riva():
    s = given(hand=["1PER19"], empty_hand=True)
    play(s, card(s, "1PER19", zone="hand"), 0)
    finish(s)
    assert len(me(s).hand) == 1 and any(i.card == "1PER19" for i in me(s).staging)


def test_old_lirpa_has_no_maximum():
    vulcans = [k for k, c in CARDS.items() if "Vulcan" in c.traits and c.set == "to_boldly_go"
               and c.suit in ("Person", "Ship") and not c.development_cost][:6]
    assert len(vulcans) == 6
    for lirpa, drawn in (("1CAR08", 6), ("2CAR11", 5)):
        s = given(hand=[lirpa], staging=vulcans, empty_hand=True)
        play(s, card(s, lirpa, zone="hand"), 0)
        assert len(me(s).hand) == drawn, lirpa


def test_old_phasers_cost_an_action_and_the_new_do_not():
    assert CARDS["1CAR11"].operations[0].action_cost and not CARDS["2CAR14"].operations[0].action_cost
    s = given(hand=["1CAR11"], empty_hand=True)
    actions = me(s).actions
    play(s, card(s, "1CAR11", zone="hand"), 0)
    finish(s)
    assert me(s).actions == actions - 1 and any(i.card == "1CAR11" for i in me(s).fleet)


def test_old_holographic_drone_ship_is_dismissed_by_an_activation():
    s = given(fleet=["1SHI04"])
    glory = me(s).glory
    activate(s, card(s, "1SHI04", zone="fleet"), 3)
    assert me(s).glory == glory + 2 and any(i.card == "1SHI04" for i in me(s).discard)


def test_old_enterprise_c_may_beam_a_card_when_played():
    s = given(hand=["1SHI09", "2PER16"], empty_hand=True)
    play(s, card(s, "1SHI09", zone="hand"), 0)
    answer(s, "Riva")
    ship = card(s, "1SHI09", zone="fleet")
    assert [b.card for b in ship.beamed] == ["2PER16"] and not ship.exhausted


def test_borg_spatial_trajector_second_play_is_never_offered():
    s = given(hand=["1CAR02"], tracks={"research": 15})
    assert can_play(s, card(s, "1CAR02", zone="hand"), 0) and not can_play(s, card(s, "1CAR02", zone="hand"), 1)


# ------------------------------------------------------------------ Allies

def test_edosians_take_one_of_two_encounters_and_log():
    s = given(hand=["1ALL05", "2PER16", "2PER17", "2PER22"], empty_hand=True, tracks={"influence": 5})
    top = [i.uid for i in s.encounter[:2]]
    left = len(s.encounter)
    play(s, card(s, "1ALL05", zone="hand"), 1)
    finish(s)
    assert len(me(s).draw) >= 3 and len(s.encounter) == left - 1
    assert any(i.uid in top for i in me(s).hand) and s.encounter[-1].uid in top
    assert me(s).log[-1].card == "1ALL05"
    s = given(hand=["1ALL05", "2PER16"], empty_hand=True, tracks={"influence": 5})
    assert not can_play(s, card(s, "1ALL05", zone="hand"), 1)  # cannot put 3 cards on the deck


def test_emerald_chain_steals_and_free_plays_a_business():
    s = given(hand=["1ALL06", "2PER22"], empty_hand=True, opp={"dilithium": 2})
    mine, theirs = me(s).dilithium, opp(s).dilithium
    play(s, card(s, "1ALL06", zone="hand"), 0)
    answer(s, "Tevrin Krit")
    finish(s)
    assert me(s).tracks["military"] == 1 and opp(s).dilithium == theirs - 1 and me(s).dilithium >= mine + 1 - 2
    assert any(i.card == "2PER22" for i in me(s).staging + me(s).fleet + me(s).discard)


def test_halkan_council_logs_itself_at_clean_up_with_an_attack_in_play():
    s = given(hand=["1ALL07"], empty_hand=True, staging=["2PER06"])  # Harry Mudd is an Attack
    dilithium = me(s).dilithium
    play(s, card(s, "1ALL07", zone="hand"), 0)
    assert me(s).dilithium == dilithium + 3
    answer(s, "End")
    finish(s)
    assert any(i.card == "1ALL07" for i in me(s).log)
    s = given(hand=["1ALL07"], empty_hand=True)
    play(s, card(s, "1ALL07", zone="hand"), 0)
    answer(s, "End")
    finish(s)
    assert not any(i.card == "1ALL07" for i in me(s).log)


def test_karemma_needs_military_and_latinum():
    s = given(hand=["1ALL08"], latinum=2, tracks={"military": 3})
    actions = me(s).actions
    play(s, card(s, "1ALL08", zone="hand"), 1)
    assert me(s).actions == actions + 1 and me(s).latinum == 1
    assert not can_play(given(hand=["1ALL08"], latinum=2), card(given(hand=["1ALL08"], latinum=2), "1ALL08", zone="hand"), 1)


def test_tholians_pay_per_controlled_location():
    s = given(hand=["1ALL13"], locations=["2LOC07", "2LOC08"])
    dilithium, latinum = me(s).dilithium, me(s).latinum
    play(s, card(s, "1ALL13", zone="hand"), 0)
    answer(s, "No")
    assert (me(s).dilithium, me(s).latinum) == (dilithium + 4, latinum + 2) and me(s).log[-1].card == "1ALL13"


# ------------------------------------------------------------------ Cargo

def test_biobed_free_plays_an_incident_or_finds_a_doctor():
    s = given(hand=["1CAR01", "2INC06"], empty_hand=True, discard=["2PER14"], latinum=1)
    play(s, card(s, "1CAR01", zone="hand"), 0)
    finish(s)  # junk, then one of the two
    s = given(hand=["1CAR01"], empty_hand=True, discard=["2PER14"])
    play(s, card(s, "1CAR01", zone="hand"), 0)
    while "Find" not in s.decision.prompt:
        answer(s, options(s)[0])
    answer(s, "Phlox")
    assert "2PER14" in hand_ids(s)


def test_ferengi_wine_counts_ferengi_and_business():
    s = given(hand=["1CAR04"], staging=["2PER17", "2PER22", "2CAR07"], tracks={"influence": 5})  # Rom; Krit; Holosuite
    latinum, glory = me(s).latinum, me(s).glory
    play(s, card(s, "1CAR04", zone="hand"), 0)
    assert me(s).latinum == latinum + 4 and me(s).glory == glory + 1  # the Wine is itself a Ferengi in play


def test_mekleth_discards_an_attack_from_the_revealed_hand():
    s = given(hand=["1CAR09", "2PER16"], empty_hand=True, opp={"hand": ["2PER06"]})
    glory = me(s).glory
    play(s, card(s, "1CAR09", zone="hand"), 0)
    assert s.decision.seat == 0 and "Harry Mudd" in options(s)
    answer(s, "Harry Mudd")
    assert me(s).tracks["military"] == 1 and me(s).glory == glory + 1
    assert any(i.card == "2PER06" for i in opp(s).discard) and "reveals their hand" in " ".join(e.text for e in s.log)


def test_tachyon_detection_grid_logs_an_opponent_cloak():
    s = given(hand=["1CAR13"], empty_hand=True, staging=["2PER11"], opp={"fleet": ["2CAR03"]})  # Reed: Security
    glory = me(s).glory
    play(s, card(s, "1CAR13", zone="hand"), 0)
    finish(s)
    assert any(i.card == "2CAR03" for i in opp(s).log) and me(s).glory == glory + 1 and me(s).tracks["military"] == 1


def test_tribbles_dismiss_klingon_duty_officers():
    s = given(hand=["1CAR14"], empty_hand=True, opp={"duty": ["2PER10"], "hand": ["2PER16"]})  # Lursa is a Klingon
    incidents = len(s.incident)
    play(s, card(s, "1CAR14", zone="hand"), 0)
    finish(s)
    assert not opp(s).duty and len(s.incident) == incidents - 1
    assert sum(1 for i in opp(s).discard if i.card in ("2PER10", "2PER16")) >= 1 and me(s).tracks["influence"] == 1


def test_unstable_wormhole_reorders_and_takes_the_top_location():
    s = given(hand=["1CAR16"], empty_hand=True)
    top = [i.uid for i in s.location_deck[:2]]
    play(s, card(s, "1CAR16", zone="hand"), 0)
    answer(s, "Location deck")
    finish(s)
    assert {i.uid for i in [s.location_deck[0], s.location_deck[1], *s.location_deck[-2:]]} >= set(top)
    assert len(me(s).hand) == 1
    s = given(hand=["1CAR16"], dilithium=3, tracks={"influence": 6})
    first = s.location_deck[0].uid
    play(s, card(s, "1CAR16", zone="hand"), 1)
    finish(s)
    assert any(i.uid == first for i in me(s).locations)
    assert not any(i.card == "1CAR16" for z in ("hand", "discard", "staging", "log") for i in getattr(me(s), z))


# ------------------------------------------------------------------ Persons

def test_necheyev_warps_any_number_of_ships():
    s = given(duty=["1PER02"], fleet=["2SHI01", "2SHI03"], dilithium=1)
    dilithium = me(s).dilithium
    activate(s, card(s, "1PER02", zone="duty"), 2)
    for _ in range(2):
        answer(s, options(s)[0])
        answer(s, options(s)[0])
    assert me(s).dilithium == dilithium - 1
    assert sum(1 for ship in me(s).fleet if ship.at) == 2


def test_pressman_dismisses_a_cloak_for_glory():
    s = given(duty=["1PER03"], fleet=["2CAR03"])
    glory = me(s).glory
    activate(s, card(s, "1PER03", zone="duty"), 2)
    assert me(s).glory == glory + 3 and me(s).log[-1].card == "1PER03"
    assert any(i.card == "2CAR03" for i in me(s).discard)
    bare = given(duty=["1PER03"])
    assert not can_activate(bare, card(bare, "1PER03", zone="duty"), 2)


def test_kamarag_returns_an_incident_when_the_opponent_takes_control():
    from engine.game import take_control

    s = given(duty=["1PER04"], hand=["2INC06"], empty_hand=True)
    take_control(s, opp(s), s.neutral[0], run_control=False)
    from engine.game import advance

    s.decision = None
    advance(s, flag_irreversible=False)
    assert s.decision.kind == "trigger"
    answer(s, "Use")
    assert not me(s).hand and s.incident[-1].card == "2INC06"


def test_b4_pays_dilithium_for_the_log():
    s = given(duty=["1PER05"], hand=["2PER16"], empty_hand=True, log=["2PER17", "2PER22", "2CAR07"])
    dilithium, incidents = me(s).dilithium, len(s.incident)
    activate(s, card(s, "1PER05", zone="duty"), 2)
    finish(s)
    assert me(s).dilithium == dilithium + 2 and len(s.incident) == incidents - 1
    assert any(CARDS[i.card].suit == "Incident" for i in opp(s).hand)


def test_maddox_finds_and_free_plays_a_synthetic():
    s = given(hand=["1PER06"], empty_hand=True, discard=["1PER17"], dilithium=2)
    play(s, card(s, "1PER06", zone="hand"), 0)
    answer(s, "Peanut Hamper")
    finish(s)
    assert any(i.card == "1PER17" for i in me(s).staging + me(s).duty)


def test_dorg_rewards_the_discarded_card():
    s = given(hand=["1PER07", "2CAR14"], empty_hand=True)  # Phasers: a Weapon without Influence or Military icons
    play(s, card(s, "1PER07", zone="hand"), 0)
    finish(s)
    owned = me(s).draw + me(s).discard
    assert any(CARDS[i.card].suit == "Ship" and CARDS[i.card].is_common for i in owned)


def test_dorg_dismisses_himself_for_an_action_after_a_shady():
    s = given(duty=["1PER07"], hand=["2PER10"], empty_hand=True)  # Lursa: Shady and Klingon
    play(s, card(s, "2PER10", zone="hand"), 0)
    seen = 0
    while s.decision.kind != "action":
        if s.decision.kind == "trigger" and any("dismiss a Klingon" in o or "Captain Dorg" in o for o in options(s)):
            seen += 1
        answer(s, next((o for o in options(s) if o.startswith("Use")), options(s)[-1]))
    assert seen


def test_joret_dal_rewards_doing_both():
    s = given(hand=["1PER09", "2PER16", "2PER17"], empty_hand=True)
    glory = me(s).glory
    play(s, card(s, "1PER09", zone="hand"), 0)
    answer(s, "Riva")
    while "Log a Person" not in s.decision.prompt:
        answer(s, options(s)[0])
    answer(s, "Rom")
    answer(s, "Yes")
    assert me(s).glory == glory + 1 and [i.card for i in me(s).duty] == ["1PER09"]
    assert me(s).log[-1].card == "2PER17" and me(s).draw[0].card == "2PER16"
    from engine.game import hand_size

    assert hand_size(s, me(s)) == 6


def test_laas_stages_a_person_and_duplicates():
    s = given(hand=["1PER10", "2PER16"], empty_hand=True, discard=["1ALL07"], )
    s.players[0].discard.append(s.new_inst("1CAR12"))  # Plasma Manifold has a PLAY, but it needs 3 Dilithium
    s.players[0].discard.append(s.new_inst("1PER17"))
    dilithium = me(s).dilithium
    assert can_play(s, card(s, "1PER10", zone="hand"), 0)
    play(s, card(s, "1PER10", zone="hand"), 0)
    assert any(i.card == "2PER16" for i in me(s).staging) and len(me(s).hand) == 0  # Riva's PLAY did not draw
    answer(s, "Gain 3")
    finish(s)
    assert me(s).dilithium == dilithium + 3
    alone = given(hand=["1PER10"], empty_hand=True)
    assert not can_play(alone, card(alone, "1PER10", zone="hand"), 0)


def test_laris_duplicates_an_earlier_resupply_and_refreshes():
    from engine.ops import start
    from engine.state import OpRef

    s = given(duty=["1PER11"], locations=["2LOC20"])  # Xahea: RESUPPLY gain 1 Dilithium
    dilithium = me(s).dilithium
    laris = card(s, "1PER11", zone="duty")
    start(s, OpRef(mode="op", seat=0, uid=laris.uid, card="1PER11", index=1))
    answer(s, "Xahea")
    assert me(s).dilithium == dilithium + 1
    s = given(duty=["1PER11"], fleet=["2SHI01"], dilithium=2)
    ship = card(s, "2SHI01", zone="fleet")
    assert not can_activate(s, card(s, "1PER11", zone="duty"), 2)  # nothing is exhausted
    ship.exhausted = True
    s.decision = None
    from engine.game import advance

    advance(s, flag_irreversible=False)
    activate(s, card(s, "1PER11", zone="duty"), 2)
    finish(s)
    assert not card(s, "2SHI01", zone="fleet").exhausted


def test_lenara_kahn_scores_anomalies_and_is_dismissed():
    s = given(duty=["1PER12"], locations=["2LOC08"], staging=["2CAR06"], latinum=1)  # Indri VIII; Forced Singularity
    glory, latinum = me(s).glory, me(s).latinum
    activate(s, card(s, "1PER12", zone="duty"), 1)
    assert me(s).glory == glory + 2 and me(s).latinum == latinum - 1 and me(s).discard[-1].card == "1PER12"


def test_lwaxana_draws_when_a_person_is_put_into_play_at_six_influence():
    for influence, drawn in ((6, 1), (5, 0)):
        s = given(duty=["1PER14"], hand=["1PER17"], empty_hand=True, tracks={"influence": influence})
        play(s, card(s, "1PER17", zone="hand"), 1)
        while s.decision.kind != "action":
            answer(s, next((o for o in options(s) if o.startswith("Use")), options(s)[-1]))
        assert len(me(s).hand) == drawn, influence


def test_mirok_forces_a_ship_into_the_log():
    s = given(hand=["1PER15", "2CAR03"], empty_hand=True, opp={"discard": ["2SHI01"]})
    glory = me(s).glory
    play(s, card(s, "1PER15", zone="hand"), 0)
    answer(s, "Cloaking Device")
    answer(s, "Borg Probe")  # the opponent chooses which Ship
    answer(s, "Yes")
    assert any(i.card == "2SHI01" for i in opp(s).log) and me(s).glory == glory + 1
    assert [i.card for i in me(s).duty] == ["1PER15"] and me(s).log[-1].card == "2CAR03"
    s = given(hand=["1PER15", "2CAR03"], empty_hand=True)
    opp(s).discard[:] = [i for i in opp(s).discard if CARDS[i.card].suit != "Ship"]
    incidents = len(s.incident)
    play(s, card(s, "1PER15", zone="hand"), 0)
    answer(s, "Cloaking Device")
    answer(s, "No")
    assert len(s.incident) == incidents - 1  # no Ship in their Discard pile: they take an Incident


def test_moriarty_makes_the_opponent_discard_two():
    s = given(hand=["1PER16"], empty_hand=True, tracks={"research": 5})
    theirs = len(opp(s).hand)
    play(s, card(s, "1PER16", zone="hand"), 0)
    finish(s)
    assert len(opp(s).hand) == theirs - 2
    low = given(hand=["1PER16"], tracks={"research": 4})
    assert not can_play(low, card(low, "1PER16", zone="hand"), 0)


def test_peanut_hamper_promotes_herself_and_flees_an_attack():
    s = given(hand=["1PER17"], empty_hand=True)
    dilithium = me(s).dilithium
    play(s, card(s, "1PER17", zone="hand"), 1)
    finish(s)
    assert me(s).dilithium == dilithium + 3 and [i.card for i in me(s).duty] == ["1PER17"]
    s = given(duty=["1PER17"], opp={"hand": ["1SHI08"]})
    s.active = 1
    s.decision = None
    from engine.game import advance, choose

    s.step = "action"
    advance(s, flag_irreversible=False)
    choose(s, 1, f"play:{card(s, '1SHI08', seat=1, zone='hand').uid}:0", flag_irreversible=False)
    while s.decision is not None and s.decision.kind != "action":
        answer(s, options(s)[0])
    assert me(s).draw[0].card == "1PER17" and not me(s).duty


def test_sakonna_badlands_play_is_never_offered():
    s = given(hand=["1PER21"], fleet=["2SHI01"], tracks={"military": 15, "influence": 15, "research": 15}, latinum=5)
    sakonna = card(s, "1PER21", zone="hand")
    assert can_play(s, sakonna, 0) and not can_play(s, sakonna, 1)
    play(s, sakonna, 0)
    answer(s, "Yes")
    finish(s)
    assert me(s).tracks["influence"] >= 15


def test_cochrane_takes_an_encounter_for_a_ship_and_three_dilithium():
    s = given(duty=["1PER25"], hand=["2SHI01"], empty_hand=True, dilithium=3)
    encounters = len(s.encounter)
    activate(s, card(s, "1PER25", zone="duty"), 1)
    assert len(s.encounter) == encounters - 1 and me(s).log[-1].card == "1PER25"
    assert any(i.card == "2SHI01" for i in me(s).staging) and not any(i.card == "2SHI01" for i in me(s).fleet)
    no_ship = given(duty=["1PER25"], empty_hand=True, dilithium=3)
    assert not can_activate(no_ship, card(no_ship, "1PER25", zone="duty"), 1)


# ------------------------------------------------------------------ Ships

def test_bird_of_prey_sends_a_team_past_ships_and_recalls_an_opponent_ship():
    s = given(hand=["1SHI01", "1SHI05"], empty_hand=True)  # K't'inga is Imperial
    glory = me(s).glory
    play(s, card(s, "1SHI01", zone="hand"), 0)
    answer(s, "Yes")
    finish(s)
    assert me(s).glory == glory + 1 and sum(loc.away.get(0, 0) for loc in s.neutral + me(s).locations) == 1
    s = given(fleet=["1SHI01"], dilithium=1, opp={"fleet": ["2SHI01"]})
    activate(s, card(s, "1SHI01", zone="fleet"), 1)
    answer(s, options(s)[0])
    answer(s, "Yes")
    assert any(i.card == "2SHI01" for i in opp(s).hand) and not opp(s).fleet


def test_sona_battlecruiser_steals():
    s = given(hand=["1SHI08"], empty_hand=True, tracks={"military": 6}, opp={"dilithium": 3})
    theirs, hand = opp(s).dilithium, len(opp(s).hand)
    play(s, card(s, "1SHI08", zone="hand"), 1)
    finish(s)
    assert opp(s).dilithium == theirs - 2 and len(opp(s).hand) == hand - 1


def test_reliant_second_play_needs_the_opponent_to_have_at_most_one_ship():
    s = given(hand=["1SHI11"], empty_hand=True, tracks={"influence": 5}, opp={"fleet": ["2SHI01", "2SHI03"]})
    assert not can_play(s, card(s, "1SHI11", zone="hand"), 1)
    s = given(hand=["1SHI11", "2KHA17"], empty_hand=True, tracks={"influence": 5}, opp={"fleet": ["2SHI01"]})
    glory = me(s).glory
    play(s, card(s, "1SHI11", zone="hand"), 1)
    answer(s, "Draw a card")
    answer(s, "Discard an Augment")
    assert me(s).glory == glory + 2 and len(me(s).hand) == 1 and any(i.card == "1SHI11" for i in me(s).fleet)


def test_voth_research_vessel_trades_a_beamed_human_for_an_encounter():
    s = given(fleet=["1SHI12"])
    ship = card(s, "1SHI12", zone="fleet")
    assert not can_activate(s, ship, 3)
    s = given(fleet=["1SHI12"])
    ship = card(s, "1SHI12", zone="fleet")
    ship.beamed.append(s.new_inst("2PER06"))  # Harry Mudd is a Human
    s.decision = None
    from engine.game import advance

    advance(s, flag_irreversible=False)
    encounters = len(s.encounter)
    activate(s, card(s, "1SHI12", zone="fleet"), 3)
    assert len(s.encounter) == encounters - 1 and me(s).log[-1].card == "1SHI12"
    assert any(i.card == "2PER06" for i in me(s).discard)
