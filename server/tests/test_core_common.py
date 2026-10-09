"""The Core Box Locations and Encounters and promo set 1 (plans/base-game.md Step 6). Specs:
resources/scans/base_game/cards/{location,encounter}/ and resources/scans/promo1/cards/."""

from engine import cards as registry
from engine.content import content
from engine.game import advance, hand_size
from engine.scoring import score_player
from engine.setup import BotSetup, SeatSetup, new_game
from engine.state import OpRef
from tests.scenario import activate, answer, can_play, card, given, options, play
from tests.test_market_cards import finish

CARDS = content().cards


def me(s):
    return s.players[0]


def opp(s):
    return s.players[1]


def refresh(s):
    s.decision = None
    advance(s, flag_irreversible=False)


def run(s, inst, index, event=None):
    """Resolve an operation that the turn loop would trigger: CONTROL, RESUPPLY or a Reaction."""
    s.decision = None
    s.op_queue.append(OpRef(mode="trigger" if event else "auto", seat=0, uid=inst.uid, index=index, event=event))
    advance(s, flag_irreversible=False)


def can_activate(s, inst, index):
    return f"activate:{inst.uid}:{index}" in {o.id for o in s.decision.options}


def test_every_core_common_and_promo_operation_has_code():
    for c in CARDS.values():
        if c.set in ("base_game", "promo1") and c.is_common and c.position != "Solo Challenge":
            for index, op in enumerate(c.operations):
                assert registry.has_code(c.id, index, op.kind), (c.id, c.name, index, op.kind)


# ------------------------------------------------------------------ Locations

def test_amargosa_observatory_rewards_a_scientist_and_evacuates_when_logged():
    s = given(locations=["1LOC01"], fleet=["2SHI01"], empty_hand=True)
    scientist = s.new_inst("1PER12")  # Lenara Kahn
    s.market["Person"] = scientist
    glory = me(s).glory
    run(s, card(s, "1LOC01", zone="locations"), 0)
    answer(s, "Lenara Kahn")
    finish(s)
    assert me(s).glory == glory + 1
    s = given(hand=["2GEO17"], locations=["1LOC01"], fleet=["2SHI01"], empty_hand=True)
    loc = card(s, "1LOC01", zone="locations")
    loc.away[0] = 1
    card(s, "2SHI01", zone="fleet").at = loc.uid
    refresh(s)
    play(s, card(s, "2GEO17", zone="hand"), 0)  # Strange New Worlds logs the selected Location
    finish(s)
    assert any(i.card == "1LOC01" for i in me(s).log)
    places = {ship.at for ship in me(s).fleet}
    assert len(places) == 1 and None not in places and loc.uid not in places  # every Ship warped to one Location


def test_baku_beams_people_and_scores_them():
    s = given(locations=["1LOC04"], duty=["2PER16"], dilithium=1)
    loc = card(s, "1LOC04", zone="locations")
    actions = me(s).actions
    activate(s, loc, 1)
    assert me(s).actions == actions + 1 and [b.card for b in loc.beamed] == ["2PER16"] and not me(s).duty
    assert registry.ENDGAME["1LOC04"](s, me(s)) == 1
    loc.exhausted = False
    refresh(s)
    activate(s, loc, 2)
    assert any(i.card == "2PER16" for i in me(s).hand) and registry.ENDGAME["1LOC04"](s, me(s)) == 0
    assert not can_activate(s, loc, 1)  # no Duty Officer left to beam


def test_corvan_ii_pays_two_for_a_card_sharing_a_trait_with_your_captain():
    for top, gained in (("2GEO02", 2), ("2PER17", 1)):  # U.S.S. Shenzhou is Starfleet like Georgiou; Rom is not
        s = given(locations=["1LOC06"])
        me(s).draw.insert(0, s.new_inst(top))
        dilithium = me(s).dilithium
        run(s, card(s, "1LOC06", zone="locations"), 1)
        assert me(s).dilithium == dilithium + gained and me(s).discard[-1].card == top


def test_deep_space_k7_needs_a_directive_or_security():
    s = given(locations=["1LOC07"], hand=["2GEO15"], empty_hand=True)  # Analyze is a Directive
    loc = card(s, "1LOC07", zone="locations")
    actions = me(s).actions
    activate(s, loc, 1)
    assert me(s).actions == actions + 1 and me(s).draw[0].card == "2GEO15"
    s = given(locations=["1LOC07"], hand=["2PER17"], empty_hand=True)
    assert not can_activate(s, card(s, "1LOC07", zone="locations"), 1)


def test_derna_scores_two_for_each_weapon_beamed_there():
    s = given(locations=["1LOC09"], hand=["2CAR14"], empty_hand=True, discard=["1CAR09"])
    loc = card(s, "1LOC09", zone="locations")
    activate(s, loc, 1)
    answer(s, "Phasers")
    loc = card(s, "1LOC09", zone="locations")  # the paused operation was replayed on a restored state
    assert [b.card for b in loc.beamed] == ["2CAR14"] and registry.ENDGAME["1LOC09"](s, me(s)) == 2
    assert score_player(s, me(s))["parts"]["endgame"] >= 2


def test_freecloud_sells_a_card_and_finds_one():
    s = given(locations=["1LOC11"], hand=["2PER16"], empty_hand=True, latinum=2)
    loc = card(s, "1LOC11", zone="locations")
    latinum = me(s).latinum
    activate(s, loc, 1)
    assert me(s).latinum == latinum + 1 and not me(s).hand


def test_regula_i_scores_anomalies_and_rewards_scientists():
    s = given(locations=["1LOC15"], hand=["1PER12"], empty_hand=True, discard=["2CAR06"], dilithium=1)
    assert registry.ENDGAME["1LOC15"](s, me(s)) == 1  # Forced Singularity is an Anomaly
    glory = me(s).glory
    play(s, card(s, "1PER12", zone="hand"), 0)  # Lenara Kahn is a Scientist
    while s.decision.kind != "action":
        answer(s, next((o for o in options(s) if o.startswith("Use")), "No"))
    assert me(s).glory == glory + 1


def test_tulgana_iv_sends_a_team_where_you_have_a_ship():
    s = given(locations=["1LOC18"], fleet=["2SHI01"], latinum=1)
    loc = card(s, "1LOC18", zone="locations")
    assert not can_activate(s, loc, 1)  # no Ship is at a Location yet
    target = s.neutral[0]
    card(s, "2SHI01", zone="fleet").at = target.uid
    refresh(s)
    activate(s, loc, 1)
    assert target.away.get(0) == 1


# ------------------------------------------------------------------ Encounters

def test_ancient_gene_fragments_draws_per_location_with_an_away_team():
    s = given(hand=["1ENC01"], empty_hand=True, locations=["2LOC07", "2LOC08"], staging=["1PER12"])
    card(s, "2LOC07", zone="locations").away[0] = 1
    actions = me(s).actions
    play(s, card(s, "1ENC01", zone="hand"), 0)
    assert len(me(s).hand) == 1 and me(s).actions == actions  # one action spent, one gained for the Scientist


def test_iconian_gateway_sends_up_to_three_teams_past_ships():
    s = given(hand=["1ENC04"], empty_hand=True, staging=["1SHI05"], opp={"fleet": ["2SHI01"]})  # K't'inga: Imperial
    target = s.neutral[0]
    card(s, "2SHI01", seat=1, zone="fleet").at = target.uid
    refresh(s)
    play(s, card(s, "1ENC04", zone="hand"), 0)
    answer(s, "3")
    answer(s, CARDS[target.card].name)
    target = next(loc for loc in s.neutral if loc.uid == target.uid)
    assert target.away.get(0) == 3 and me(s).tracks["military"] == 1


def test_omega_particle_is_destroyed_at_five_borg():
    s = given(hand=["1ENC06"], empty_hand=True, staging=["2SHI01"] * 5)  # five Borg Probes
    glory = me(s).glory
    play(s, card(s, "1ENC06", zone="hand"), 0)
    assert me(s).glory == glory + 5
    assert not any(i.card == "1ENC06" for z in ("hand", "staging", "discard", "log") for i in getattr(me(s), z))
    s = given(hand=["1ENC06"], empty_hand=True)
    play(s, card(s, "1ENC06", zone="hand"), 0)
    assert any(i.card == "1ENC06" for i in me(s).staging)


def test_sha_ka_ree_becomes_a_controlled_location():
    """REQ-CORE-50: it is a Location for all purposes, and deploying it counts as taking control."""
    s = given(hand=["1ENC07", "2SHI01"], empty_hand=True, duty=["2PER11"])
    incidents = len(s.incident)
    play(s, card(s, "1ENC07", zone="hand"), 0)
    answer(s, "Borg Probe")
    finish(s)
    shakaree = card(s, "1ENC07", zone="locations")
    assert [b.card for b in shakaree.beamed] == ["2SHI01"] and len(s.incident) == incidents - 2
    assert sum(1 for i in opp(s).hand if CARDS[i.card].suit == "Incident") == 2
    kept = given(hand=["1ENC07"], empty_hand=True)
    play(kept, card(kept, "1ENC07", zone="hand"), 0)
    finish(kept)
    answer(kept, "End")
    finish(kept)
    assert any(i.card == "1ENC07" for i in me(kept).locations)  # it stays in play after Clean-up, like a Location


def test_sha_ka_ree_counts_as_taking_control():
    s = given(deck="kirk", hand=["1ENC07"], empty_hand=True)
    play(s, card(s, "1ENC07", zone="hand"), 0)
    assert any(e for e in s.log if "takes control of Sha Ka Ree" in e.text)


# ------------------------------------------------------------------ promo set 1

def test_enterprise_b_sends_a_team_only_on_a_tuesday():
    """CORE-AS-7 (REQ-CORE-53): the weekday comes from the command, never from the clock."""
    for weekday, teams in ((1, 1), (2, 0), (None, 0)):
        s = given(hand=["0SHI01", "2PER16"], empty_hand=True)
        s.weekday = weekday
        glory = me(s).glory
        play(s, card(s, "0SHI01", zone="hand"), 0)
        if weekday == 1:
            answer(s, "Yes")
        finish(s)
        assert me(s).glory == glory + 1 and any(i.card == "0SHI01" for i in me(s).fleet)
        assert sum(loc.away.get(0, 0) for loc in s.neutral + me(s).locations) == teams, weekday


def test_enterprise_b_logs_a_person_for_a_card_and_an_action():
    s = given(fleet=["0SHI01"], staging=["2PER16"], empty_hand=True)
    actions = me(s).actions
    activate(s, card(s, "0SHI01", zone="fleet"), 3)
    assert me(s).actions == actions + 1 and len(me(s).hand) == 1 and me(s).log[-1].card == "2PER16"


def test_sehlat_plays_and_promotes_vulcans():
    vulcan = next(k for k, c in CARDS.items() if c.suit == "Person" and "Vulcan" in c.traits and c.is_common
                  and c.set == "to_boldly_go")
    s = given(hand=["0CAR01", vulcan], empty_hand=True)
    sehlat = card(s, "0CAR01", zone="hand")
    assert can_play(s, sehlat, 1) and can_play(s, sehlat, 2)
    play(s, sehlat, 2)
    assert [i.card for i in me(s).duty] == [vulcan]
    bare = given(hand=["0CAR01", "2PER17"], empty_hand=True)
    assert not can_play(bare, card(bare, "0CAR01", zone="hand"), 1)


def test_wesley_crusher_is_a_person_and_lends_staged_people_their_activations():
    """REQ-CORE-51."""
    s = given(hand=["2CAR13"], staging=["0ENC01"], empty_hand=True)
    wesley = card(s, "0ENC01", zone="staging")
    from engine.ops import Actions, Ctx

    acts = Actions(Ctx(s, OpRef(mode="auto", seat=0)), ["PROMOTE"])
    for _ in acts.promote(wesley):
        pass
    assert [i.card for i in me(s).duty] == ["0ENC01"]
    harry = s.new_inst("2PER06")  # Harry Mudd: ACTIVATION "Dismiss this card to recall a non-Time Travel card"
    me(s).staging.extend([harry, s.new_inst("2PER17")])
    refresh(s)
    assert can_activate(s, harry, 1)
    without = given(staging=["2PER06", "2PER17"], empty_hand=True)
    assert not can_activate(without, card(without, "2PER06", zone="staging"), 1)


def test_flight_training_accident_needs_a_pilot_for_its_second_play():
    pilot = next(k for k, c in CARDS.items() if "Pilot" in c.traits and c.suit == "Person" and c.set == "to_boldly_go")
    s = given(hand=["0INC01"], staging=[pilot], empty_hand=True)
    glory = me(s).glory
    play(s, card(s, "0INC01", zone="hand"), 1)
    assert me(s).glory == glory + 1 and s.incident[-1].card == "0INC01"
    bare = given(hand=["0INC01"], empty_hand=True)
    assert not can_play(bare, card(bare, "0INC01", zone="hand"), 1)


def test_whale_probe_incursion_recalls_ships_on_both_sides():
    s = given(hand=["0INC02"], empty_hand=True, fleet=["2SHI01"], opp={"fleet": ["2SHI03"]})
    me(s).fleet[:] = [i for i in me(s).fleet if i.card == "2SHI01"]
    opp(s).fleet[:] = [i for i in opp(s).fleet if i.card == "2SHI03"]
    refresh(s)
    play(s, card(s, "0INC02", zone="hand"), 0)
    finish(s)
    assert any(i.card == "2SHI01" for i in me(s).hand) and any(i.card == "2SHI03" for i in opp(s).hand)
    assert any(i.card == "0INC02" for i in me(s).staging)  # no Creature: it is not returned


def test_promo_incident_surprises_run_for_the_bot():
    from engine import bot as bot_rules

    for card_id in ("0INC01", "0INC02"):
        s = new_game(3, "solo", [SeatSetup("Me", "kirk", "basic")], [], False, bot=BotSetup("soval", "admiral"))
        advance(s, flag_irreversible=False)
        bot = s.players[1]
        inst = s.new_inst(card_id)
        bot.staging.append(inst)
        s.decision = None
        bot_rules.queue_resolution(s, bot, inst)
        advance(s, flag_irreversible=False)
        while s.decision is not None and not (s.decision.kind == "action" and s.decision.seat == 0):
            answer(s, options(s)[0])
        assert s.incident[-1].card == card_id, card_id
        if card_id == "0INC01":
            assert s.players[1].glory >= 1 and "at once" in " ".join(e.text for e in s.log)


# ------------------------------------------------------------------ promo sets in setup

def test_the_promo_option_adds_both_sets_and_old_games_keep_promo_set_two():
    seats = [SeatSetup("A", "kirk", "basic"), SeatSetup("B", "soval", "basic")]
    old = new_game(5, "two_player", seats, promos=True)
    assert old.promo_sets == ["promo2"]
    new = new_game(5, "two_player", seats, promos=True, promo_sets=["promo1", "promo2"])
    everything = [i.card for d in new.market_decks.values() for i in d] + [i.card for i in new.market.values() if i] \
        + [i.card for i in new.encounter + new.incident]
    assert {"0SHI01", "0CAR01", "0ENC01", "0INC01", "0INC02", "0INC03"} <= set(everything)
    assert len(new.incident) == 6  # REQ-CORE-52: each promo Incident replaced a different one
    assert sum(1 for i in new.incident if CARDS[i.card].set == "to_boldly_go") == 3
    assert not any(c.startswith("0") and CARDS[c].set == "promo1" for c in [i.card for i in old.incident])


def test_combined_boxes_cut_incidents_before_the_promos_replace_any():
    """REQ-CORE-23."""
    seats = [SeatSetup("A", "kirk", "basic"), SeatSetup("B", "soval", "basic")]
    for seed in range(6):
        s = new_game(seed, "two_player", seats, promos=True, promo_sets=["promo1", "promo2"], box="both")
        ids = [i.card for i in s.incident]
        assert len(ids) == 6 and {"0INC01", "0INC02", "0INC03"} <= set(ids), seed


def test_hand_size_is_unchanged_by_these_cards():
    s = given(locations=["1LOC04", "1LOC09"])
    assert hand_size(s, me(s)) == 5
