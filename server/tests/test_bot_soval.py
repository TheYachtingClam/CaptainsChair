"""The Soval Bot (plans/solo-mode.md Step 2): its Automated Command rows, and the solo rulebook's complete Bot turn
(requirements/22-solo-mode.md §13), the acceptance test for the Bot runtime."""

from engine import bot as bot_rules
from engine.bot.actions import BotActions, card_matches, parse_wanted
from engine.content import content
from engine.game import advance, choose
from engine.ops import A, Ctx
from engine.setup import BotSetup, SeatSetup, new_game
from engine.state import OpRef

CARDS = content().cards


def solo(deck="kirk", difficulty="admiral", seed=7):
    s = new_game(seed, "solo", [SeatSetup("Me", deck, "basic")], ["second_contact"], False,
                 bot=BotSetup("soval", difficulty))
    advance(s, flag_irreversible=False)
    return s


def me(s):
    return s.players[0]


def the_bot(s):
    return s.players[1]


def options(s):
    return [o.label for o in s.decision.options]


def answer(s, text):
    option = next(o for o in s.decision.options if text in o.label)
    choose(s, s.decision.seat, option.id, flag_irreversible=False)


def log_text(s):
    return " | ".join(e.text for e in s.log)


def resolve_card(s, card_id, *, side=None):
    """Put a card in the Bot's Staging Area and resolve it as the Bot, outside its turn."""
    bot = the_bot(s)
    if side:
        bot.bot.suits_side = side
    inst = s.new_inst(card_id)
    bot.staging.append(inst)
    s.decision = None
    bot_rules.queue_resolution(s, bot, inst)
    advance(s, flag_irreversible=False)
    return inst


def test_gain_descriptions_parse_with_precedence():
    assert parse_wanted("A > B / C") == [["A"], ["B", "C"]]
    assert parse_wanted("A / B > C") == [["A", "B"], ["C"]]
    s = solo()
    riva, tpol = s.new_inst("2PER16"), s.new_inst("2SOV21")
    assert card_matches(riva, "[Influence]") and card_matches(riva, "[Influence Focus]")
    assert not card_matches(riva, "[Research]") and card_matches(tpol, "[Research]")
    assert card_matches(tpol, "Person") and card_matches(tpol, "Scientist")


def test_rows_declare_their_actions():
    s = solo()
    bot = the_bot(s)
    actions = BotActions(Ctx(s, OpRef(mode="bot", seat=1)), [A.LOG], s.new_inst("2PER07"), lambda i: iter(()))
    try:
        list(actions.gain_glory(1))
    except Exception as err:
        assert "did not declare" in str(err)
    else:
        raise AssertionError("an undeclared Bot action must fail")
    _ = bot


def test_every_soval_row_has_code():
    crew = content().command["soval"]
    for side in crew.sides:
        for r in side.rows:
            if "Surprise" in r.matches:
                continue
            assert ("soval", side.side, r.number) in bot_rules.ROWS, (side.side, r.number)


def test_row_actions_match_the_spec():
    """Each Bot row declares exactly the actions its spec lists (resources/scans/<set>/command/<crew>.md)."""
    for (crew, side, number), impl in bot_rules.ROWS.items():
        spec = next(r for r in content().command[crew].side(side).rows if r.number == number)
        assert set(spec.uses) == set(impl.uses), (crew, side, number, set(spec.uses) ^ set(impl.uses))


def test_wildcard_matches_the_first_trait_row():
    s = solo()
    me(s).hand.append(s.new_inst("2INC05"))
    resolve_card(s, "2ENC04")  # an Encounter with the printed Wildcard trait
    assert "matches Telepath (row 2 of TRAITS)" in log_text(s)


def test_location_with_no_trait_row_uses_the_suits_row_then_goes_to_the_control_area():
    s = solo()
    bot = the_bot(s)
    paan = resolve_card(s, "2SOV11")
    assert "matches Location (row 8 of SUITS WITH NO DUTY OFFICER)" in log_text(s)
    assert any(i.uid == paan.uid for i in the_bot(s).locations) and bot.glory >= 0


def test_incidents_are_returned_instead_of_logged():
    s = solo()
    bot = the_bot(s)
    bot.draw.insert(0, s.new_inst("2INC02"))  # Hostile Contact on top of the Bot deck
    resolve_card(s, "2INC03")  # Incident row: log the top card of the Bot deck
    assert not any(CARDS[i.card].suit == "Incident" for i in the_bot(s).log)


def test_path_of_surak_is_discarded_instead_of_logged():
    s = solo()
    the_bot(s).draw.insert(0, s.new_inst("2SOV19"))  # Infinite Diversity: Path of Surak
    resolve_card(s, "2INC03")
    assert any(i.card == "2SOV19" for i in the_bot(s).discard) and "special rule" in log_text(s)


def test_promoting_flips_the_suits_card_and_a_new_officer_replaces_the_old():
    s = solo()
    resolve_card(s, "2PER11")  # a Person: the Person row promotes it
    bot = the_bot(s)
    assert [i.card for i in bot.duty] == ["2PER11"] and bot.bot.suits_side == "with_duty_officer"
    the_bot(s).bot.suits_side = "no_duty_officer"
    resolve_card(s, "2PER14")
    bot = the_bot(s)
    assert [i.card for i in bot.duty] == ["2PER14"] and any(i.card == "2PER11" for i in bot.discard)


def test_dismissing_the_officer_flips_back():
    s = solo()
    resolve_card(s, "2PER11")
    resolve_card(s, "2CAR14", side="with_duty_officer")  # Cargo row with a Duty Officer: dismiss it
    bot = the_bot(s)
    assert not bot.duty and bot.bot.suits_side == "no_duty_officer"


def test_attack_row_at_nine_military_takes_control():
    s = solo()
    the_bot(s).tracks["military"] = 9
    target = bot_rules.most_valuable(s, list(s.neutral), the_bot(s))
    resolve_card(s, "2SOV15")  # Stel: Attack
    bot = the_bot(s)
    assert any(i.uid == target.uid for i in bot.locations) and any(i.card == "2SOV15" for i in bot.log)


def test_away_teams_are_not_sent_past_more_enough():
    s = solo()
    bot = the_bot(s)
    loc = s.neutral[0]
    loc.away[1] = 4
    ctx = Ctx(s, OpRef(mode="bot", seat=1))
    actions = BotActions(ctx, [A.SEND_AWAY_TEAM], s.new_inst("2PER07"), lambda i: iter(()))
    assert not actions.can_send_to(loc)  # 4 tokens and 4 ahead: more than enough (REQ-SOLO-161, -162)
    _ = bot


# ------------------------------------------------------------------ requirements/22-solo-mode.md §13

def test_solo_rulebook_complete_bot_turn():
    s = solo(deck="kirk")
    human, bot = me(s), the_bot(s)
    data = content()

    # The Stardate shows 4 Bot actions and 2 Glory: the Scientist row takes one, Glory placement empties it, and the
    # next one holds 6.
    s.stardates = [s.new_inst(c) for c in ("SD30", "SD31", "SD32")]
    s.stardate_glory = 2
    # The Bot: Influence 8 (Riva is worth 4 to it), Military 4.
    bot.tracks.update(research=2, influence=8, military=4)
    bot.highest.update(research=2, influence=8, military=4)
    # The human: Influence multiplier x2 (Riva is worth 2 to them), an Incident to return.
    human.tracks["influence"] = human.highest["influence"] = 2
    assert data.boards[human.board].multiplier("influence", 2) == 2
    human.hand.append(s.new_inst("2INC05"))

    # The Bot deck: the four cards for this turn, then Political Crisis and Infinite Diversity.
    bot.draw = [s.new_inst(c) for c in ("2SOV21", "2SOV15", "2ENC06", "2SOV11", "2INC03", "2SOV19")] + bot.draw
    bot.reserve.insert(0, s.new_inst("2SOV10"))  # Seleya on top of the Supplement deck
    bot.duty, bot.locations, bot.fleet, bot.staging = [], [], [], []

    # The Market: Hoshi Sato (Riva next in the Person deck), EVA Suit, Xindi-Aquatic Cruiser, Vidiians with 1 Glory.
    s.market = {"Person": s.new_inst("2PER07"), "Cargo": s.new_inst("2CAR05"), "Ship": s.new_inst("2SHI12"),
                "Ally": s.new_inst("2ALL16")}
    s.market["Ally"].res["glory"] = 1
    filler_ally = next(k for k, c in data.cards.items() if c.is_common and c.suit == "Ally" and isinstance(c.vp, int)
                       and c.vp >= 2 and "Starfleet" not in c.traits and not c.focus)
    s.market_decks["Person"].insert(0, s.new_inst("2PER16"))  # Riva
    s.market_decks["Ally"].insert(0, s.new_inst(filler_ally))
    s.market_decks["Cargo"].insert(0, s.new_inst("3CAR02"))  # Moopsy: 2 VP
    for inst in s.market.values():
        assert not card_matches(inst, "[Research Focus]")

    # The Neutral Zone: Delta Vega (a human Ship and Away Team), Indri VIII (1 Bot Away Team), and a busier third.
    delta, indri, third = s.new_inst("2LOC05"), s.new_inst("2LOC08"), s.neutral[0]
    s.neutral = [delta, indri, third]
    ship = human.fleet[0]
    ship.at = delta.uid
    delta.away = {0: 1}
    indri.away = {1: 1}
    third.away = {0: 2}
    human.away_pool -= 3
    bot.away_pool -= 1

    # The Bot's turn.
    s.active, s.step, s.substep, s.decision = 1, "bot", "control", None
    advance(s, flag_irreversible=False)
    text = log_text(s)
    assert "has not secured a Location" in text  # 1. Control Step: nothing happens
    assert "has 4 action(s) and draws 4 card(s) facedown" in text  # 2.

    # 3. Card 1, Sub-Commander T'Pol: the Telepath row offers the human an Incident return.
    assert s.decision.seat == 0 and "return an Incident" in s.decision.prompt
    answer(s, "Subspace Phenomenon")
    # Political Crisis (Incident row): Infinite Diversity is discarded (special rule), Hoshi gained, Riva revealed.
    # T'Pol is promoted, then continue resolution: the Scientist row takes Vidiians (worth 4 like Riva, but with a
    # Glory token on it).
    # 4. Card 2, Stel (Attack row, Military 4): the human removes an Away Team.
    assert s.decision.seat == 0 and "Remove one of your Away Teams" in s.decision.prompt
    answer(s, "Delta Vega")
    text = log_text(s)
    assert "matches Telepath (row 2 of TRAITS)" in text
    assert "matches Incident (row 1 of SUITS WITH NO DUTY OFFICER)" in text
    assert "discards Infinite Diversity in Infinite Combinations instead of logging it" in text
    assert "gains Hoshi Sato to its Discard pile" in text and "Riva is revealed" in text
    assert "promotes Sub-Commander T'Pol" in text and "matches Scientist / Anomaly (row 3 of TRAITS)" in text
    assert "takes Vidiians onto its deck" in text

    advance(s, flag_irreversible=False)
    while s.decision.seat != 0 or s.decision.kind != "action":
        assert s.decision.seat == 0
        answer(s, s.decision.options[0].label)
    bot, human = the_bot(s), me(s)
    text = log_text(s)
    assert "cannot send an Away Team there" in text and "matches Attack (row 6 of TRAITS)" in text
    assert bot.tracks["military"] >= 6  # +2 at Stel (the Seleya Ship row adds 1 more)

    # 5. Card 3, Species 10-C: the Encounter row with a Duty Officer; the Supplement's Seleya resolves (Ship row with
    # a Duty Officer): deploys, explores to Indri VIII (tied with Delta Vega on tokens, more valuable), gains 1
    # Military, sends an Away Team to Indri VIII, which secures it.
    assert "matches Encounter (row 7 of SUITS WITH DUTY OFFICER)" in text
    assert "matches Ship (row 2 of SUITS WITH DUTY OFFICER)" in text
    assert "Seleya (D'Kyr) explores to Indri VIII" in text
    indri = next(loc for loc in s.neutral if loc.card == "2LOC08")
    seleya = next(i for i in bot.fleet if i.card == "2SOV10")
    assert seleya.at == indri.uid and indri.away.get(1) == 2
    from engine.game import secured_by

    assert secured_by(s, indri, bot.seat)
    assert any(i.card == "2ENC06" for i in bot.log)
    # 6. Card 4, Paan Mokar: no trait row; the Location row with a Duty Officer gains EVA Suit (the only Starfleet),
    # logs T'Pol (SUITS flips back), and Paan Mokar goes to the Control Area.
    assert "matches Location (row 8 of SUITS WITH DUTY OFFICER)" in text
    assert "gains EVA Suits to its Discard pile" in text
    assert any(i.card == "2SOV21" for i in bot.log) and bot.bot.suits_side == "no_duty_officer"
    assert any(i.card == "2SOV11" for i in bot.locations)
    assert bot.tracks["military"] == 7 and bot.tracks["research"] == 3 and bot.tracks["influence"] == 10
    # 7. Clean-up: Stel is discarded; Glory goes on Riva, the leftmost of the cards worth 2 to the human. That empties
    # the Stardate card, which goes to the human's Staging Area; the next one holds 6 Glory.
    assert any(i.card == "2SOV15" for i in bot.discard) and not bot.staging
    assert "places 1 Glory on Riva" in text
    assert any(i.card == "SD30" for i in human.received_stardates)
    assert s.stardates[0].card == "SD31" and s.stardate_glory == 6


def test_cancelled_bot_attack_skips_only_the_attack_part():
    """REQ-SOLO-182, -184: Riva's "when you would be attacked" Reaction cancels the red part (removing your Away
    Team); the rest of the row still resolves, and here the failed removal gains the Bot 2 Military."""
    s = solo()
    human = me(s)
    human.duty.append(s.new_inst("2PER16"))  # Riva
    loc = s.neutral[0]
    loc.away[0] = 1
    military = the_bot(s).tracks["military"]
    resolve_card(s, "2SOV15")  # Stel: Attack row
    assert s.decision.seat == 0 and "Reaction" in s.decision.prompt
    answer(s, "Riva")
    while s.decision.kind != "action":
        answer(s, s.decision.options[0].label)  # the card Riva discards
    assert s.neutral[0].away.get(0) == 1  # nothing removed
    assert the_bot(s).tracks["military"] == military + 2
    assert "ignores the negative effect" in log_text(s)


def test_the_view_gives_the_latest_bot_turn_as_steps():
    from engine.views import game_view

    s = solo()
    choose(s, 0, "end", flag_irreversible=False)
    while s.decision is not None and not (s.decision.kind == "action" and s.decision.seat == 0):
        d = s.decision
        choose(s, d.seat, {"discard": "done"}.get(d.kind, d.options[0].id), flag_irreversible=False)
    turn = game_view(s, 0)["bot_turn"]
    assert turn["finished"] and turn["steps"][0]["text"].startswith("Turn 2: Soval Bot")
    flips = [st for st in turn["steps"] if "flips" in st["text"] and "SUITS card" not in st["text"]]
    assert flips and all("card" in st for st in flips)
    matches = [st for st in turn["steps"] if "row" in st]
    assert matches and {"side", "number"} <= set(matches[0]["row"])
    sides = game_view(s, 0)["players"][1]["bot"]["command"]
    assert [x["side"] for x in sides if x["up"]] == ["traits", the_bot(s).bot.suits_side] and len(sides) == 3
