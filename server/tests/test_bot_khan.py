"""The Khan Bot (requirements/15-crew-decks.md REQ-CD-KHN-11; resources/scans/to_boldly_go/command/khan.md): its setup,
the KHAN IN EXILE card, trait marking, its rows, Khan's four SURPRISE operations and its scoring."""

from engine import bot as bot_rules
from engine.content import content
from engine.game import advance, choose
from engine.scoring import score_player
from engine.setup import BotSetup, SeatSetup, new_game
from engine.views import game_view

CARDS = content().cards
ROW_TRAITS = {"Surprise", "Mind Control", "Augment", "Ops", "Creature", "Scientist", "Attack", "Wildcard"}
BOARD = {"Ambassador", "Business", "Cloak", "Creature", "Doctor", "Engineer", "Scientist", "Spy", "Synthetic", "Telepath"}


def solo(deck="kirk", bot="khan", seed=5, exile=True):
    s = new_game(seed, "solo", [SeatSetup("Me", deck, "basic")], [], False, bot=BotSetup(bot, "admiral"))
    advance(s, flag_irreversible=False)
    if not exile:
        the_bot(s).bot.exile = False
    return s


def me(s):
    return s.players[0]


def the_bot(s):
    return s.players[1]


def log_text(s):
    return " | ".join(e.text for e in s.log)


def resolve_card(s, card_id, *, side=None):
    bot = the_bot(s)
    if side:
        bot.bot.suits_side = side
    inst = s.new_inst(card_id)
    bot.staging.append(inst)
    s.decision = None
    bot_rules.queue_resolution(s, bot, inst)
    advance(s, flag_irreversible=False)
    return inst


def finish(s, prefer=()):
    while s.decision is not None and not (s.decision.kind == "action" and s.decision.seat == 0):
        options = s.decision.options
        pick = next((o for p in prefer for o in options if p in o.label), None)
        if pick is None and s.decision.kind == "trigger":
            pick = next(o for o in options if "Do not" in o.label)
        choose(s, s.decision.seat, (pick or options[0]).id, flag_irreversible=False)


def common(suit, *, having=(), without=ROW_TRAITS):
    return next(k for k, c in CARDS.items() if c.is_common and c.set == "to_boldly_go" and c.suit == suit
                and set(having) <= set(c.traits) and not set(without) & set(c.traits))


def everything(bot):
    return [*bot.draw, *bot.reserve, *bot.discard, *bot.staging, *bot.locations, *bot.fleet, *bot.duty, *bot.log]


# ------------------------------------------------------------------ setup

def test_setup_removes_ceti_alpha_and_buries_genesis_device():
    s = solo()
    bot = the_bot(s)
    ids = {i.card for i in everything(bot)}
    assert not ids & {"2KHA02A", "2KHA02B", "2KHA03"}
    assert bot.reserve[-1].card == "2KHA11" and len(bot.reserve) == 8  # every Development; Khan has no Reserves
    assert bot.captain.card == "2KHA01A" and bot.bot.exile


def test_solo_challenge_card_goes_on_top_of_the_supplement_deck():
    s = new_game(5, "solo", [SeatSetup("Me", "kirk", "basic")], [], False,
                 bot=BotSetup("khan", "admiral", ticking_clock=True))
    reserve = s.players[1].reserve
    assert reserve[0].card == "2DIR01" and reserve[-1].card == "2KHA11"


def test_the_view_shows_only_the_exile_card_until_it_is_replaced():
    s = solo()
    view = game_view(s, 0)["players"][1]["bot"]
    assert view["exile"] and [c["side"] for c in view["command"] if c["up"]] == ["exile_traits"]
    the_bot(s).bot.exile = False
    view = game_view(s, 0)["players"][1]["bot"]
    assert [c["side"] for c in view["command"] if c["up"]] == ["traits", "no_duty_officer"]


# ------------------------------------------------------------------ KHAN IN EXILE

def test_exile_ends_at_five_dilithium_at_the_end_of_the_turn():
    """Spec test: with 5 Dilithium at the end of its turn, it spends them, gains the top Encounter and switches."""
    s = solo()
    bot = the_bot(s)
    end = bot_rules.END_OF_TURN["khan"]
    end(s, bot)
    assert bot.dilithium == 1 and bot.bot.exile
    bot.dilithium = 4
    top = s.encounter[0]
    end(s, bot)
    assert bot.dilithium == 0 and not bot.bot.exile
    assert bot.discard[-1].uid == top.uid and s.encounter[0].uid != top.uid
    end(s, bot)
    assert bot.dilithium == 0  # the exile card's rule is gone with the card


def test_a_whole_bot_turn_in_exile_gains_a_dilithium():
    s = solo()
    choose(s, 0, "end", flag_irreversible=False)
    finish(s)  # your Clean-up, then the Bot's whole turn
    assert s.active == 0 and s.turn >= 2
    assert the_bot(s).dilithium >= 1 and "gains 1 Dilithium (Khan in Exile)" in log_text(s)


def test_exile_augment_row():
    s = solo()
    bot = the_bot(s)
    resolve_card(s, "2KHA17")  # Wajahut: Ops, Human, Augment
    text = log_text(s)
    assert "matches Augment (row 2 of KHAN IN EXILE)" in text and "sends an Away Team" in text
    assert "takes an Incident" in text and sum(loc.away.get(1, 0) for loc in s.neutral) == 1
    assert any(CARDS[i.card].suit == "Person" for i in bot.discard)


def test_exile_rows_match_suits_and_a_played_location_stays_out_of_the_control_area():
    s = solo()
    bot = the_bot(s)
    top = bot.draw[0]
    played = resolve_card(s, "2KHA14")  # Mutara Nebula, played from the Bot deck
    assert "matches Person / Cargo / Ally / Location (row 6 of KHAN IN EXILE)" in log_text(s)
    assert any(i.uid == top.uid for i in bot.discard)
    assert not bot.locations and any(i.uid == played.uid for i in bot.staging)
    assert "gains an Incident" not in log_text(s)


def test_exile_location_taken_in_the_control_step_costs_an_incident_and_a_dilithium():
    s = solo()
    bot = the_bot(s)
    loc = s.neutral.pop(0)
    bot.locations.append(loc)
    bot.dilithium = 2
    s.decision = None
    bot_rules.queue_resolution(s, bot, loc)
    advance(s, flag_irreversible=False)
    assert bot.dilithium == 1 and CARDS[bot.discard[-1].card].suit == "Incident"
    assert any(i.uid == loc.uid for i in bot.locations)


def test_exile_person_gains_glory_from_the_supply():
    s = solo()
    stardate = s.stardate_glory
    resolve_card(s, "2KHA13")  # Marla McGivers: no trait row
    assert the_bot(s).glory == 1 and s.stardate_glory == stardate


def test_an_encounter_matches_nothing_in_exile():
    s = solo()
    resolve_card(s, "2ENC01")
    assert "matches no Automated Command row" in log_text(s)


def test_a_card_leaving_the_supplement_deck_in_exile_gains_a_dilithium():
    """The new Bot deck gets the top Supplement card even though Khan's Captain says he does not enlist: the Bot
    ignores its card text (REQ-SOLO-61, -80)."""
    s = solo()
    bot = the_bot(s)
    bot.discard.extend(bot.draw)
    bot.draw = []
    supplement = bot.reserve[0]
    drawn = bot_rules.draw_card(s, bot)
    assert drawn.uid == supplement.uid and bot.dilithium == 1 and len(bot.reserve) == 7
    bot.bot.exile = False
    bot.discard.extend(bot.draw)
    bot.draw = []
    bot_rules.draw_card(s, bot)
    assert bot.dilithium == 1 and len(bot.reserve) == 6


# ------------------------------------------------------------------ trait marking

def test_the_bot_marks_the_first_unmarked_trait_of_a_gained_card():
    s = solo(exile=False)
    bot = the_bot(s)
    ship_id = next(k for k, c in CARDS.items() if c.is_common and c.suit == "Ship" and len(BOARD & set(c.traits)) == 1
                   and not {"Starfleet", "Human", "Wildcard"} & set(c.traits))
    ship = s.new_inst(ship_id)
    s.market["Ship"] = ship
    before = bot_rules.value(s, ship, bot)
    resolve_card(s, "2KHA14")  # Location with no Duty Officer: discard 2, gain a Ship
    assert any(i.uid == ship.uid for i in bot.discard)
    expected = next(t for t in sorted(BOARD) if t in CARDS[ship_id].traits)
    assert [m.trait for m in bot.marks][:1] == [expected]
    assert bot_rules.value(s, ship, bot) == before - 3  # worth 3 more only while it has an unmarked trait


def test_mark_a_trait_goes_in_board_order_then_the_opponent_entries():
    s = solo(exile=False)
    bot = the_bot(s)
    for _ in range(12):
        assert bot_rules.mark_trait(s, bot)
    assert [m.slot for m in bot.marks][:3] == ["ambassador", "business", "cloak"]
    assert {m.trait for m in bot.marks[-2:]} == {"Starfleet", "Human"}  # against Kirk (REQ-CD-KHN-09)
    assert not bot_rules.mark_trait(s, bot)


def test_other_bots_never_mark():
    s = solo(bot="soval")
    assert not bot_rules.mark_trait(s, the_bot(s)) and not the_bot(s).marks


def test_unmarked_locations_are_preferred():
    s = solo(exile=False)
    bot = the_bot(s)
    marked_all = [loc for loc in s.neutral]
    target = s.new_inst(next(k for k, c in CARDS.items() if c.is_common and c.suit == "Location"
                             and BOARD & set(c.traits)))
    s.neutral = [loc for loc in marked_all if not bot_rules.unmarked(s, bot, loc)][:2] + [target]
    resolve_card(s, "2KHA17")  # Augment / Ops row
    assert target.away.get(1) == 1


# ------------------------------------------------------------------ TRAITS

def test_mind_control_gains_two_glory_when_you_have_no_duty_officer_and_continues():
    s = solo(exile=False)
    bot = the_bot(s)
    terrell = resolve_card(s, "2KHA06")  # Cpt. Terrell: Mind Control, Person
    finish(s)
    text = log_text(s)
    assert "matches Mind Control (row 2 of TRAITS)" in text and "(row 5 of SUITS WITH NO DUTY OFFICER)" in text
    assert bot.glory == 3 and [i.uid for i in bot.duty] == [terrell.uid]
    assert bot.bot.suits_side == "with_duty_officer"


def test_mind_control_dismisses_your_duty_officer():
    s = solo(exile=False)
    bot, human = the_bot(s), me(s)
    officer = s.new_inst(common("Person"))
    human.duty.append(officer)
    resolve_card(s, "2KHA08")  # Ceti Eel: Mind Control, then Creature
    finish(s)
    assert not human.duty and any(i.uid == officer.uid for i in human.discard)
    assert bot.glory == 0 and "matches Creature / Scientist (row 4 of TRAITS)" in log_text(s)


def test_creature_sends_two_away_teams_to_one_location_and_logs():
    s = solo(exile=False)
    bot = the_bot(s)
    incident = s.new_inst("2INC01")
    bot.discard.append(incident)
    eel = resolve_card(s, "2KHA08")
    finish(s)
    assert max(loc.away.get(1, 0) for loc in s.neutral) == 2
    assert any(i.uid == incident.uid for i in s.incident) and any(i.uid == eel.uid for i in bot.log)


def test_augment_person_takes_an_incident_and_a_person():
    s = solo(exile=False)
    bot = the_bot(s)
    resolve_card(s, "2KHA18")  # Joachim
    suits = [CARDS[i.card].suit for i in bot.draw[:2]]
    assert suits == ["Person", "Incident"] and "(row 3 of TRAITS)" in log_text(s)


def test_augment_ship_discards_the_top_supplement_card():
    s = solo(exile=False)
    bot = the_bot(s)
    top = bot.reserve[0]
    resolve_card(s, "2KHA04")  # Hijacked U.S.S. Reliant
    assert bot.discard[-1].uid == top.uid


def test_attack_row_gives_you_an_incident_from_the_bot_discard_pile():
    s = solo(exile=False)
    bot, human = the_bot(s), me(s)
    incident = s.new_inst("2INC01")
    bot.discard.append(incident)
    attack = resolve_card(s, "2KHA05")  # Surprise Attack
    finish(s)
    assert [m.slot for m in bot.marks] == ["ambassador"]
    assert any(i.uid == incident.uid for i in human.hand) and not human.log
    assert any(i.uid == attack.uid for i in bot.log)


def test_attack_row_otherwise_you_find_and_log_a_card():
    s = solo(exile=False)
    bot, human = the_bot(s), me(s)
    owned = len(human.hand) + len(human.draw) + len(human.discard) + len(human.reserve)
    resolve_card(s, "2KHA05")
    finish(s)
    bot, human = the_bot(s), me(s)  # the paused operation was replayed on a restored state
    assert len(human.log) == 1
    assert len(human.hand) + len(human.draw) + len(human.discard) + len(human.reserve) == owned - 1
    assert bot.log


def test_revenge_is_logged_by_you():
    s = solo(exile=False)
    bot, human = the_bot(s), me(s)
    revenge = resolve_card(s, "2KHA10")
    finish(s)
    bot, human = the_bot(s), me(s)
    assert any(i.uid == revenge.uid for i in human.log) and not any(i.uid == revenge.uid for i in everything(bot))


# ------------------------------------------------------------------ SUITS

def test_incident_row_gains_glory_for_a_trait_shared_with_your_captain():
    s = solo(exile=False)
    bot = the_bot(s)
    bot.draw.insert(0, s.new_inst("2KHA12"))  # Vacated Regula I: Starfleet, as Kirk is
    incident = resolve_card(s, common("Incident"))
    assert bot.glory == 1 and any(i.uid == incident.uid for i in s.incident)
    bot.draw.insert(0, s.new_inst("2KHA16"))  # S.S. Botany Bay: only Human
    resolve_card(s, common("Incident"))
    assert bot.glory == 1


def test_incident_row_with_a_duty_officer_gives_you_the_incident():
    s = solo(exile=False)
    bot, human = the_bot(s), me(s)
    bot.duty.append(s.new_inst("2KHA13"))
    incident = resolve_card(s, common("Incident"), side="with_duty_officer")
    finish(s)
    assert any(i.uid == incident.uid for i in human.hand)


def test_ally_takes_a_spy_cloak_or_synthetic_else_gains_a_person_or_ship():
    s = solo(exile=False)
    bot = the_bot(s)
    wanted = {"Spy", "Cloak", "Synthetic", "Wildcard"}
    for suit, inst in list(s.market.items()):
        while inst is not None and wanted & set(CARDS[inst.card].traits):
            inst = s.market[suit] = s.market_decks[suit].pop(0)
    ally = resolve_card(s, common("Ally", without=ROW_TRAITS))
    assert CARDS[bot.discard[-1].card].suit in ("Person", "Ship") and any(i.uid == ally.uid for i in bot.log)
    spy_id = next(k for k, c in CARDS.items() if c.is_common and c.suit in s.market and "Spy" in c.traits)
    spy = s.new_inst(spy_id)
    s.market[CARDS[spy_id].suit] = spy
    resolve_card(s, common("Ally", without=ROW_TRAITS))
    assert bot.draw[0].uid == spy.uid


def test_person_with_a_duty_officer_puts_an_augment_on_the_deck_and_dismisses():
    s = solo(exile=False)
    bot = the_bot(s)
    officer, augment = s.new_inst("2KHA13"), s.new_inst("2KHA17")
    bot.duty.append(officer)
    bot.discard.append(augment)
    resolve_card(s, "2KHA13", side="with_duty_officer")
    assert bot.draw[0].uid == augment.uid and not bot.duty and bot.bot.suits_side == "no_duty_officer"


def test_encounter_with_eight_marks_gains_the_best_of_three_and_logs_it():
    s = solo(exile=False)
    bot = the_bot(s)
    bot.duty.append(s.new_inst("2KHA13"))
    for _ in range(8):
        bot_rules.mark_trait(s, bot)
    top = [i.uid for i in s.encounter[:3]]
    left = len(s.encounter)
    this = resolve_card(s, "2ENC01", side="with_duty_officer")
    logged = {i.uid for i in bot.log}
    assert len(s.encounter) == left - 3 and len(logged & set(top)) == 1 and this.uid in logged
    assert not {i.uid for i in everything(bot)} & (set(top) - logged)  # the other two are destroyed


def test_encounter_with_fewer_marks_resolves_the_top_supplement_card():
    s = solo(exile=False)
    bot = the_bot(s)
    bot.duty.append(s.new_inst("2KHA13"))
    top = bot.reserve[0]
    resolve_card(s, "2ENC01", side="with_duty_officer")
    finish(s)
    assert "resolves " + CARDS[top.card].name + " at once" in log_text(s)


# ------------------------------------------------------------------ SURPRISE operations

def test_khans_incident_surprise_goes_to_your_discard_pile_and_you_draw():
    for card_id in ("2KHA19", "2KHA20", "2KHA21"):
        s = solo(exile=False)
        bot, human = the_bot(s), me(s)
        top, hand = bot.draw[0], len(human.hand)
        curse = resolve_card(s, card_id)
        finish(s)
        assert "resolves its SURPRISE operation" in log_text(s) and "(row" not in log_text(s)
        assert any(i.uid == top.uid for i in bot.discard)
        assert any(i.uid == curse.uid for i in human.discard) and len(human.hand) == hand + 1


def test_two_dimensional_thinking_is_returned_when_the_bot_has_an_augment():
    s = solo(exile=False)
    human = me(s)
    ship = s.new_inst("2SHI01")
    human.fleet.append(ship)
    card = resolve_card(s, "2KHA22")
    assert "warp one of your Ships?" in s.decision.prompt and s.decision.seat == 0
    finish(s, prefer=(CARDS[ship.card].name,))
    assert next(i for i in me(s).fleet if i.uid == ship.uid).at is not None
    assert any(i.uid == card.uid for i in s.incident) and "(row" not in log_text(s)


def test_two_dimensional_thinking_continues_resolution_for_a_bot_without_an_augment():
    s = solo(deck="khan", bot="kirk")
    card = resolve_card(s, "2KHA22")
    finish(s)
    assert "matches Incident (row 1 of SUITS WITH NO DUTY OFFICER)" in log_text(s)
    assert not any(i.uid == card.uid for i in the_bot(s).staging)


# ------------------------------------------------------------------ scoring

def test_the_bot_scores_three_for_each_marked_trait_and_each_focus_icon():
    s = solo(exile=False)
    bot = the_bot(s)
    base = score_player(s, bot)
    assert base["parts"]["traits"] == 0
    bot_rules.mark_trait(s, bot)
    bot_rules.mark_trait(s, bot)
    focus = next(k for k, c in CARDS.items() if c.is_common and c.focus == "Research")
    bot.discard.append(s.new_inst(focus))
    parts = score_player(s, bot)["parts"]
    assert parts["traits"] == 6 and parts["focus_research"] == 3
    assert "traits" not in score_player(s, me(s))["parts"]
