"""The six Core Box Bots, the Burnham Bot's special rule and Conspiracy (plans/base-game.md Step 13)."""

import pytest

from engine import bot as bot_rules
from engine import cards as registry
from engine.bot.actions import SUITS
from engine.content import content
from engine.game import advance, choose
from engine.scoring import score_player
from engine.setup import BotSetup, SeatSetup, SetupError, new_game

CARDS = content().cards
CORE = ["picard", "shran", "koloth", "sela", "sisko", "burnham"]


def solo(bot, deck="kirk", seed=5, **kw):
    s = new_game(seed, "solo", [SeatSetup("Me", deck, "basic")], [], False, bot=BotSetup(bot, "admiral", **kw),
                 box="both")
    advance(s, flag_irreversible=False)
    return s


def me(s):
    return s.players[0]


def the_bot(s):
    return s.players[1]


def answer(s, text):
    option = next(o for o in s.decision.options if text in o.label)
    choose(s, s.decision.seat, option.id, flag_irreversible=False)


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
        opts = [o.label for o in s.decision.options]
        pick = next((o for p in prefer for o in opts if p in o), None)
        if s.decision.kind == "trigger" and pick is None:
            pick = next((o for o in opts if "Do not" in o), None)
        answer(s, pick or opts[0])


def with_officer(s, card_id="1BUR05"):
    bot = the_bot(s)
    bot.duty.append(s.new_inst(card_id))
    bot.bot.suits_side = "with_duty_officer"


def rows_used(s):
    return [(e.row["side"], e.row["number"]) for e in s.log if e.row]


# ------------------------------------------------------------------ every row runs

def card_for(crew, side, row):
    """A card whose first matching row is this one."""
    traits_side = content().command[crew].side("traits")
    earlier, every = set(), set()
    for r in traits_side.rows:
        if side == "traits" and r.number < row.number:
            earlier |= set(r.matches)
        every |= set(r.matches)
    for c in CARDS.values():
        traits = set(c.traits)
        if c.set != "base_game" or c.suit not in SUITS or traits & {"Surprise", "Wildcard"} or c.id.endswith("B"):
            continue
        if side == "traits":
            if traits & set(row.matches) and not traits & earlier:
                return c.id
        elif c.suit in row.matches and not traits & every:
            return c.id
    return None


ROWS = [(crew, side.side, r.number) for crew in CORE for side in content().command[crew].sides for r in side.rows
        if "Surprise" not in r.matches and side.side in ("traits", "no_duty_officer", "with_duty_officer")]


@pytest.mark.parametrize("crew,side,number", ROWS)
def test_every_row_runs(crew, side, number):
    row = next(r for r in content().command[crew].side(side).rows if r.number == number)
    card_id = card_for(crew, side, row)
    if card_id is None:
        pytest.skip(f"no Core Box card resolves through {crew} {side} {number}")
    for seed in (3, 8):
        s = solo(crew, seed=seed)
        bot = the_bot(s)
        bot.tracks.update(research=6, influence=6, military=9)
        if side == "with_duty_officer":
            with_officer(s)
        s.neutral[0].away[1] = 2
        s.neutral[0].away[0] = 1
        resolve_card(s, card_id, side=side if side != "traits" else None)
        finish(s)
        assert (side, number) in rows_used(s), (card_id, rows_used(s))


# ------------------------------------------------------------------ Picard and Shran

def test_picard_klingon_row_removes_your_away_team_or_pays_the_bot():
    s = solo("picard")
    bot = the_bot(s)
    for loc in s.neutral:
        loc.away[0] = 1
    glory = bot.glory
    resolve_card(s, "1KOL14")  # Mara, a Klingon
    finish(s)
    assert sum(loc.away.get(0, 0) for loc in s.neutral) == len(s.neutral) - 1 and bot.glory == glory
    s = solo("picard")
    bot = the_bot(s)
    resolve_card(s, "1KOL14")
    finish(s)
    assert bot.glory == 1 and any(CARDS[i.card].suit == "Incident" for i in bot.draw[:1])


def test_shran_weapon_row_gives_you_the_choice():
    s = solo("shran")
    s.neutral[0].away[0] = 1
    hand = len(me(s).hand)
    resolve_card(s, "1CAR08")  # Lirpa, a Weapon
    finish(s, prefer=("Remove one of your Away Teams",))
    assert s.neutral[0].away.get(0, 0) == 0 and len(me(s).hand) == hand
    s = solo("shran")
    resolve_card(s, "1CAR08")
    finish(s)
    assert any(CARDS[i.card].suit == "Incident" for i in me(s).hand)  # no Away Team: only the Incident


def test_shran_attack_row_discards_the_top_of_your_deck():
    s = solo("shran")
    bot = the_bot(s)
    me(s).draw.insert(0, s.new_inst("1BUR05"))  # a Person
    resolve_card(s, "1PER15")  # Mirok, an Attack Person
    finish(s)
    assert me(s).discard[-1].card == "1BUR05" and any(CARDS[i.card].suit == "Incident" for i in me(s).hand)
    assert CARDS[bot.draw[0].card].suit == "Incident" and bot.tracks["military"] == 0
    assert [i.card for i in bot.duty] == ["1PER15"]
    s = solo("shran")
    me(s).draw.insert(0, s.new_inst("1CAR04"))  # not a Person
    resolve_card(s, "1PER15")
    finish(s)
    assert the_bot(s).tracks["military"] == 1 and not any(CARDS[i.card].suit == "Incident" for i in me(s).hand)


# ------------------------------------------------------------------ Koloth

def test_koloth_weapon_row_cashes_in_a_klingon_duty_officer():
    s = solo("koloth")
    bot = the_bot(s)
    bot.tracks["military"] = 8
    with_officer(s, "1KOL14")  # Mara, a Klingon
    resolve_card(s, "1CAR08")
    finish(s)
    assert not bot.duty and bot.glory == 4 and bot.bot.suits_side == "no_duty_officer"
    assert any(i.card == "1CAR08" for i in bot.log)
    s = solo("koloth")
    bot = the_bot(s)
    s.neutral[0].away[0] = 1
    resolve_card(s, "1CAR08")
    finish(s)
    assert s.neutral[0].away.get(0, 0) == 0 and bot.tracks["military"] == 1
    s = solo("koloth")
    resolve_card(s, "1CAR08")
    finish(s)
    assert the_bot(s).tracks["military"] == 2  # nothing to remove


def test_koloth_attack_row():
    s = solo("koloth")
    bot = the_bot(s)
    bot.discard.append(s.new_inst("1PIC14"))
    fleet = len(me(s).fleet)
    resolve_card(s, "1PER15")
    finish(s)
    assert bot.draw[0].card == "1PIC14" and len(me(s).fleet) == fleet
    s = solo("koloth")
    assert me(s).fleet
    resolve_card(s, "1PER15")
    finish(s)
    assert not me(s).fleet and the_bot(s).glory == 0  # no Ship in its Discard pile: you dismiss yours
    s = solo("koloth")
    me(s).fleet.clear()
    resolve_card(s, "1PER15")
    finish(s)
    assert the_bot(s).glory == 1


def test_koloth_takes_the_top_of_the_supplement_deck():
    s = solo("koloth")
    bot = the_bot(s)
    top = bot.reserve[0].uid
    logged = bot.draw[0].uid
    resolve_card(s, "1CAR05")  # Forced Singularity is Romulan
    finish(s)
    assert bot.draw[0].uid == top and any(i.uid == logged for i in [*bot.log, *s.incident])


def test_koloth_incident_row_lets_you_draw():
    s = solo("koloth")
    hand = len(me(s).hand)
    resolve_card(s, "1INC01")
    finish(s, prefer=("Yes",))
    assert len(me(s).hand) == hand + 1


def test_koloth_ally_row_with_an_officer_gives_you_a_discarded_incident():
    s = solo("koloth")
    bot = the_bot(s)
    for suit in list(s.market):
        s.market[suit] = None  # no Romulan to gain
    with_officer(s)
    resolve_card(s, "1ALL02", side="with_duty_officer")
    finish(s)
    assert CARDS[me(s).discard[-1].card].suit == "Incident" and not bot.duty and bot.glory == 1


def test_koloth_directive_row_with_an_officer_trades_a_ship_for_an_encounter():
    s = solo("koloth")
    bot = the_bot(s)
    with_officer(s)
    bot.fleet.append(s.new_inst("1KOL02"))
    s.neutral[0].away[1] = 1
    encounter = s.encounter[0].uid
    resolve_card(s, "1BUR17", side="with_duty_officer")
    finish(s)
    assert bot.draw[0].uid == encounter and not bot.fleet and not bot.duty
    assert s.neutral[0].away.get(1, 0) == 0


# ------------------------------------------------------------------ Sela

def test_sela_shady_row_takes_control_at_eight_military():
    s = solo("sela")
    bot = the_bot(s)
    bot.tracks["military"] = 7
    target = s.neutral[1]
    target.away[1] = 2
    target.away[0] = 3
    glory = me(s).glory
    resolve_card(s, "1ALL10")  # Letheans are Shady
    finish(s)
    assert any(i.uid == target.uid for i in [*bot.locations, *bot.log, *bot.discard])
    assert any(i.card == "1ALL10" for i in bot.log) and me(s).glory >= glory
    s = solo("sela")
    bot = the_bot(s)
    resolve_card(s, "1ALL10")
    finish(s)
    assert bot.tracks["military"] == 2 and bot.tracks["influence"] == 1


def test_sela_cloak_row():
    s = solo("sela")
    bot = the_bot(s)
    pool = bot.away_pool
    resolve_card(s, "1SEL03")  # I.R.W. Valdore
    finish(s)
    assert any(i.card == "1SEL03" for i in bot.fleet) and bot.away_pool == pool - 1
    s = solo("sela")
    resolve_card(s, "1CAR03")  # Cloaking Device
    finish(s)
    assert the_bot(s).glory == 3 and any(i.card == "1CAR03" for i in the_bot(s).log)


def test_sela_klingon_row_is_your_choice():
    s = solo("sela")
    resolve_card(s, "1KOL14")
    finish(s, prefer=("Dismiss one of your Ships",))
    assert not me(s).fleet
    s = solo("sela")
    top = the_bot(s).draw[2].uid  # the row first discards 2
    resolve_card(s, "1KOL14")
    finish(s, prefer=("The Bot resolves",))
    assert me(s).fleet and not any(i.uid == top for i in the_bot(s).draw)


def test_sela_attack_row():
    s = solo("sela")
    bot = the_bot(s)
    bot.tracks["military"] = 8
    me(s).duty.append(s.new_inst("1BUR05"))
    me(s).locations.append(s.new_inst("1BUR09"))
    resolve_card(s, "1PER15")
    finish(s, prefer=("Dismiss a Duty Officer", "Log one of your controlled Locations"))
    assert not me(s).duty and any(CARDS[i.card].suit == "Location" for i in me(s).log)
    assert any(i.card == "1PER15" for i in the_bot(s).log)
    s = solo("sela")
    hand = len(me(s).hand)
    resolve_card(s, "1PER15")
    finish(s)
    assert len(me(s).hand) == hand + 1 and not the_bot(s).log  # only the Incident; under 8 Military nothing more


def test_sela_person_row_dismisses_a_ship_when_nothing_else_can_be_gained():
    s = solo("sela")
    bot = the_bot(s)
    for suit in list(s.market):
        if s.market[suit] is not None and set(CARDS[s.market[suit].card].traits) & {"Vulcan", "Klingon"}:
            s.market[suit] = None
    bot.fleet.append(s.new_inst("1SEL02"))
    resolve_card(s, "1BUR05", side="no_duty_officer")
    finish(s)
    assert not bot.fleet and [i.card for i in bot.duty] == ["1BUR05"] and bot.tracks["military"] == 1


def test_sela_directive_row_gains_the_encounter_to_the_discard_pile():
    s = solo("sela")
    bot = the_bot(s)
    with_officer(s)
    s.neutral[0].away[1] = 2
    encounter = s.encounter[0].uid
    resolve_card(s, "1BUR17", side="with_duty_officer")
    finish(s)
    assert any(i.uid == encounter for i in bot.discard) and not bot.duty and s.neutral[0].away.get(1, 0) == 0


# ------------------------------------------------------------------ Sisko

def test_sisko_starbase_row_deploys_deep_space_9_without_exploring():
    s = solo("sisko")
    bot = the_bot(s)
    resolve_card(s, "1SIS03")
    finish(s)
    ds9 = next(i for i in bot.fleet if i.card == "1SIS03")
    assert ds9.at is None


def test_sisko_bajoran_row():
    s = solo("sisko")
    bot = the_bot(s)
    bot.discard.append(s.new_inst("1ALL02"))
    pool = bot.away_pool
    resolve_card(s, "1CAR10")  # Orb of Time is Bajoran
    finish(s)
    assert bot.away_pool == pool - 2 and max(loc.away.get(1, 0) for loc in s.neutral) == 2
    s = solo("sisko")
    bot = the_bot(s)
    me(s).duty.append(s.new_inst("1BUR05"))
    resolve_card(s, "1CAR10")
    finish(s)
    assert not me(s).duty and bot.tracks["military"] == 3 and bot.tracks["influence"] == 1


def test_books_ship_saves_your_officer_from_the_sisko_bot():
    s = solo("sisko", deck="burnham")
    me(s).duty.append(s.new_inst("1BUR05"))
    ship = s.new_inst("1BUR15")
    ship.beamed.append(s.new_inst("1CAR04"))
    me(s).fleet.append(ship)
    resolve_card(s, "1CAR10")
    finish(s, prefer=("Use Book's Ship",))
    assert [i.card for i in me(s).duty] == ["1BUR05"] and not next(i for i in me(s).fleet if i.card == "1BUR15").beamed


def test_sisko_attack_row_prefers_a_starbase():
    s = solo("sisko")
    resolve_card(s, "1PER15")
    finish(s)
    sent = next(loc for loc in s.neutral if loc.away.get(1))
    bases = [loc for loc in s.neutral if "Starbase" in CARDS[loc.card].traits]
    assert (sent in bases or not bases) and the_bot(s).tracks["military"] == 2
    assert bases, "seed 5 has a Starbase in the Neutral Zone"


def test_sisko_ship_row_with_an_officer_logs_a_starbase_for_a_supplement_card():
    s = solo("sisko")
    bot = the_bot(s)
    with_officer(s)
    bot.fleet.append(s.new_inst("1SIS03"))
    top = bot.reserve[0].uid
    resolve_card(s, "1PIC14", side="with_duty_officer")
    finish(s)
    bot = the_bot(s)
    assert any(i.card == "1SIS03" for i in bot.log) and not any(i.uid == top for i in bot.reserve)
    assert any(i.card == "1PIC14" for i in bot.fleet)


def test_sisko_directive_row_never_logs_a_starbase():
    s = solo("sisko")
    bot = the_bot(s)
    with_officer(s)
    bot.locations.append(s.new_inst("1LOC07"))
    s.neutral[0].away[1] = 2
    resolve_card(s, "1BUR17", side="with_duty_officer")
    finish(s)
    assert any(i.card == "1LOC07" for i in bot.locations) and not bot.duty and bot.tracks["influence"] == 1


# ------------------------------------------------------------------ Burnham

def test_burnham_bot_has_no_inert_dilithium():
    s = solo("burnham")
    assert not the_bot(s).status


def test_burnham_bot_clean_up_places_dilithium():
    s = solo("burnham")
    bot = the_bot(s)
    s.stardate_glory = 4
    glory_on_cards = sum(i.res.get("glory", 0) for i in s.market.values() if i)
    bot_rules._cleanup(s, bot)
    cards = [i for i in s.market.values() if i]
    assert s.stardate_glory == 3 and sum(i.res.get("dilithium", 0) for i in cards) == 2
    assert sum(i.res.get("glory", 0) for i in cards) == glory_on_cards


def test_burnham_bot_scores_each_dilithium():
    s = solo("burnham")
    bot = the_bot(s)
    bot.dilithium, bot.latinum = 5, 3
    assert score_player(s, bot)["parts"]["resources"] == 6
    other = solo("picard")
    the_bot(other).dilithium, the_bot(other).latinum = 5, 3
    assert score_player(other, the_bot(other))["parts"]["resources"] == 4


def test_burnham_bot_gains_the_card_with_the_most_dilithium():
    s = solo("burnham")
    bot = the_bot(s)
    s.market["Ship"].res["glory"] = 3
    rich = s.market["Cargo"]
    rich.res["dilithium"] = 2
    resolve_card(s, "1CAR04", side="no_duty_officer")  # a plain Cargo
    finish(s)
    assert any(i.uid == rich.uid for i in bot.discard) and bot.dilithium == 2
    s = solo("burnham")
    glorious = s.market["Ship"]
    glorious.res["glory"] = 3
    resolve_card(s, "1CAR04", side="no_duty_officer")
    finish(s)
    assert any(i.uid == glorious.uid for i in the_bot(s).discard) and the_bot(s).glory == 3


def test_burnham_bot_directive_row_removes_a_glory():
    s = solo("burnham")
    s.stardate_glory = 4
    resolve_card(s, "1BUR17", side="no_duty_officer")
    finish(s)
    assert s.stardate_glory == 3 and the_bot(s).glory == 0 and the_bot(s).tracks["influence"] == 2


def test_burnham_bot_uses_cards_from_its_discard_pile():
    s = solo("burnham")
    bot = the_bot(s)
    bot.discard += [s.new_inst("1PIC14"), s.new_inst("1BUR05")]
    resolve_card(s, "1CAR07")  # Horta, a Creature
    finish(s)
    ship = next(i for i in bot.fleet if i.card == "1PIC14")
    assert ship.at is not None and bot.tracks["military"] == 1
    resolve_card(s, "1ALL11")  # Organians, an Anomaly
    finish(s)
    assert [i.card for i in bot.duty] == ["1BUR05"] and bot.glory >= 2


# ------------------------------------------------------------------ Conspiracy (REQ-SOLO-132, CORE-AS-8)

def conspiracy_of(player):
    return [i for z in (player.hand, player.draw, player.discard, player.reserve, player.log, player.staging)
            for i in z if i.card == "1DIR01"]


def test_conspiracy_joins_the_supplement_deck():
    s = solo("picard", conspiracy=True)
    assert [i.card for i in the_bot(s).reserve].count("1DIR01") == 1 and the_bot(s).bot.conspiracy
    both = solo("picard", conspiracy=True, ticking_clock=True)
    assert {"1DIR01", "2DIR01"} <= {i.card for i in the_bot(both).reserve}
    with pytest.raises(SetupError):
        new_game(1, "solo", [SeatSetup("Me", "kirk", "basic")], [], False, bot=BotSetup("soval", conspiracy=True))


def test_conspiracy_surprise_is_your_choice():
    s = solo("picard")
    bot = the_bot(s)
    reserve = len(bot.reserve)
    resolve_card(s, "1DIR01")
    answer(s, "The Bot gains 2 Glory")
    finish(s)
    bot = the_bot(s)
    assert bot.glory == 2 and len(bot.reserve) == reserve - 1 and conspiracy_of(bot)
    s = solo("picard")
    resolve_card(s, "1DIR01")
    answer(s, "Take an Incident")
    finish(s)
    assert [i.card for i in me(s).draw[-1:]] == ["1DIR01"] and CARDS[me(s).draw[-2].card].suit == "Incident"
    assert the_bot(s).glory == 0 and not conspiracy_of(the_bot(s))


def before_scoring(s):
    from engine.game import end_turn

    s.last_turn = s.turn
    s.decision = None
    end_turn(s)
    advance(s, flag_irreversible=False)
    finish(s)


def test_core_as_8_conspiracy_is_destroyed_before_scoring_when_the_bot_owns_it():
    s = solo("picard", conspiracy=True)
    before_scoring(s)
    assert not conspiracy_of(the_bot(s))


def test_conspiracy_costs_you_four_points_unless_you_log_it():
    s = solo("picard")
    card = s.new_inst("1DIR01")
    me(s).hand.append(card)
    assert registry.VP_SPECIAL["1DIR01"](s, me(s), card) == -4
    before = score_player(s, me(s))["total"]
    me(s).hand.remove(card)
    assert score_player(s, me(s))["total"] == before + 4
    me(s).log.append(card)
    before_scoring(s)
    assert not conspiracy_of(me(s))


def test_conspiracy_cannot_be_discarded_or_beamed():
    from tests.scenario import given

    s = given(deck="burnham", hand=["1DIR01"], empty_hand=True)
    assert not any(o.id.startswith("activate") and "beam" in o.label.lower() for o in s.decision.options)
    choose(s, 0, "end", flag_irreversible=False)
    while s.decision.kind != "discard":
        choose(s, 0, {"control": "skip"}.get(s.decision.kind, s.decision.options[0].id), flag_irreversible=False)
    assert [o.id for o in s.decision.options] == ["done"]
    choose(s, 0, "done", flag_irreversible=False)
    assert any(i.card == "1DIR01" for i in s.players[0].hand)


def test_conspiracy_play_discards_it():
    from tests.scenario import card, given, play

    s = given(deck="burnham", hand=["1DIR01", "1BUR05"], empty_hand=True)
    play(s, card(s, "1DIR01", zone="hand"), 0)
    p = s.players[0]
    assert [i.card for i in p.discard[-2:]] == ["1BUR05", "1DIR01"] and len(p.hand) == 1


def test_mekleth_gains_no_glory_against_the_bot():
    """Decision 2026-10-09: the Bot has no hand, so no Attack is discarded and the Glory is not gained."""
    s = solo("picard")
    human = me(s)
    human.hand[:] = [s.new_inst("1CAR09"), s.new_inst("1CAR04")]
    s.decision = None
    advance(s, flag_irreversible=False)
    blade = next(i for i in me(s).hand if i.card == "1CAR09")
    glory = me(s).glory
    choose(s, 0, f"play:{blade.uid}:0", flag_irreversible=False)
    while s.decision is not None and s.decision.kind != "action":
        opts = [o.label for o in s.decision.options]
        answer(s, next((o for o in opts if "succeeded" in o), opts[0]))
    assert me(s).glory == glory and me(s).tracks["military"] == 1
