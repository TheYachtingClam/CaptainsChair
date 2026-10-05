"""Solo mode against the Bot, plans/solo-mode.md Step 1: setup, the value function, the Bot's turn with a placeholder
card resolution, its deck, and scoring (requirements/22-solo-mode.md §1 to §5)."""

import pytest

from engine import bot as bot_rules
from engine.content import content
from engine.game import advance, choose
from engine.ops import A, Actions, Ctx
from engine.scoring import score_game, score_player
from engine.setup import BotSetup, SeatSetup, SetupError, new_game
from engine.state import OpRef

CARDS = content().cards


def solo(deck="kirk", bot="soval", difficulty="ensign", ticking_clock=False, seed=3):
    s = new_game(seed, "solo", [SeatSetup("Me", deck, "basic")], ["second_contact"], False,
                 bot=BotSetup(bot, difficulty, ticking_clock))
    advance(s, flag_irreversible=False)
    return s


def me(s):
    return s.players[0]


def the_bot(s):
    return s.players[1]


def end_my_turn(s):
    """End the human's Action Step and answer the Clean-up, leaving the game at the next human decision."""
    choose(s, 0, "end", flag_irreversible=False)
    while s.decision is not None and s.decision.kind != "action":
        d = s.decision
        choose(s, d.seat, {"discard": "done"}.get(d.kind, d.options[0].id), flag_irreversible=False)


# ------------------------------------------------------------------ setup (REQ-SOLO-20 to -33)

def test_setup():
    s = solo(difficulty="admiral", ticking_clock=True)
    human, bot = me(s), the_bot(s)
    assert s.first_seat == 0 and s.active == 0  # the human goes first
    assert all(CARDS[i.card].mode == "Solo vs Admiral Bot" for i in s.stardates)
    assert bot.bot.crew == "soval" and bot.board == "cb-soval-basic" and bot.bot.suits_side == "no_duty_officer"
    assert (bot.dilithium, bot.latinum, bot.glory, bot.actions, bot.mission_tokens) == (0, 0, 0, 0, 0)
    assert not bot.hand and not bot.status and not bot.development  # no hand; Status back in the box
    supplement = [CARDS[i.card].position for i in bot.reserve]
    assert "2DIR01" in [i.card for i in bot.reserve]  # Ticking Clock
    # Reserves (and Time Is Running Out) on top of the Developments
    first_dev = supplement.index("Development")
    assert all(p == "Development" for p in supplement[first_dev:])
    assert bot.away_pool == CARDS[bot.captain.card].away_teams
    assert len(human.hand) == 5


def test_bot_deck_has_deployed_and_location_cards_on_top():
    s = solo(bot="pike")  # Starbase One is Pike's Controlled Location
    top = [CARDS[i.card].position for i in the_bot(s).draw[:1]]
    assert top == ["Controlled Location"]


def test_khan_bot_waits():
    with pytest.raises(SetupError):
        new_game(1, "solo", [SeatSetup("Me", "kirk", "basic")], [], False, bot=BotSetup("khan"))
    with pytest.raises(SetupError):
        new_game(1, "solo", [SeatSetup("Me", "kirk", "basic")], [], False)


# ------------------------------------------------------------------ value (REQ-SOLO-40 to -43)

def test_value_counts_vp_focus_endgame_and_glory():
    s = solo()
    bot = the_bot(s)
    tpau = s.new_inst("2SOV06")  # T'Pau: 4 VP
    assert bot_rules.value(s, tpau, bot) == 4
    riva = s.new_inst("2PER16")  # Riva: Influence Focus
    bot.tracks["influence"] = bot.highest["influence"] = 10
    multiplier = content().boards[bot.board].multiplier("influence", 10)
    assert bot_rules.value(s, riva, bot) == multiplier
    riva.res["glory"] = 2
    riva.res["dilithium"] = 3  # other resources do not count
    assert bot_rules.value(s, riva, bot) == multiplier + 2
    endgame = next(k for k, c in CARDS.items() if c.is_common and any(o.kind == "ENDGAME" for o in c.operations))
    assert bot_rules.value(s, s.new_inst(endgame), bot) >= 5


def test_value_ties_prefer_more_tokens_then_leftmost():
    s = solo()
    bot = the_bot(s)
    a, b, c = (s.new_inst("2PER07") for _ in range(3))  # same card: same value
    assert bot_rules.most_valuable(s, [a, b, c], bot) is a  # leftmost
    assert bot_rules.least_valuable(s, [a, b, c], bot) is a
    b.res["dilithium"] = 1
    assert bot_rules.most_valuable(s, [a, b, c], bot) is b  # more tokens is more valuable
    assert bot_rules.least_valuable(s, [b, a, c], bot) is a  # fewer tokens is less valuable


# ------------------------------------------------------------------ the Bot's turn (REQ-SOLO-50 to -61)

def test_bot_turn_draws_its_actions_and_places_glory():
    s = solo(difficulty="admiral")
    bot = the_bot(s)
    actions = bot_rules.bot_actions(s)
    assert actions == CARDS[s.stardates[0].card].bot_actions and actions > 0
    deck = len(bot.draw)
    market = {suit: dict(i.res) for suit, i in s.market.items() if i}
    stardate = s.stardate_glory
    end_my_turn(s)
    assert s.active == 0 and s.turn == 2  # the Bot took its turn without asking anything
    assert len(bot.draw) <= deck - actions or bot.discard  # drawn (or reshuffled)
    assert not bot.staging and not bot.bot.facedown  # Staging Area discarded
    log = " ".join(e.text for e in s.log)
    assert f"has {actions} action(s)" in log and "places 1 Glory" in log
    placed = [suit for suit, i in s.market.items() if i and i.res.get("glory", 0) > market.get(suit, {}).get("glory", 0)]
    assert placed or s.stardate_glory != stardate


def test_bot_glory_goes_on_the_card_least_valuable_to_the_human():
    s = solo()
    human = me(s)
    cards = bot_rules.market_cards(s)
    expected = bot_rules.least_valuable(s, cards, human)
    before = expected.res.get("glory", 0)
    s.active = 1
    bot = the_bot(s)
    s.step, s.substep = "bot", "cleanup"
    s.decision = None
    bot_rules._cleanup(s, bot)
    assert expected.res.get("glory", 0) == before + 1


def test_bot_deck_reshuffles_and_adds_the_supplement_top():
    s = solo()
    bot = the_bot(s)
    bot.discard = [s.new_inst("2PER07"), s.new_inst("2PER11")]
    bot.draw = []
    top_supplement = bot.reserve[0]
    drawn = bot_rules.draw_card(s, bot)
    assert drawn is top_supplement and len(bot.draw) == 2 and not bot.discard


def test_bot_takes_control_of_its_most_valuable_secured_location():
    s = solo()
    bot = the_bot(s)
    loc = s.neutral[0]
    loc.away[1] = 3
    bot.away_pool -= 3
    s.active = 1
    s.step, s.substep = "bot", "control"
    bot_rules.step_bot(s)
    assert loc in bot.locations and loc not in s.neutral and bot.away_pool == CARDS[bot.captain.card].away_teams


def test_bot_location_goes_to_the_control_area():
    s = solo()
    bot = the_bot(s)
    location = s.new_inst("2SOV11")  # Paan Mokar
    bot.staging.append(location)
    s.decision = None
    bot_rules.queue_resolution(s, bot, location)
    advance(s, flag_irreversible=False)
    bot = the_bot(s)  # rebuilt by the operation's replay
    assert any(i.uid == location.uid for i in bot.locations) and not bot.staging


def test_bot_facedown_cards_are_hidden():
    from engine.views import game_view

    s = solo()
    bot = the_bot(s)
    inst = s.new_inst("2PER07")
    bot.staging.append(inst)
    bot.bot.facedown.append(inst.uid)
    view = game_view(s, 0)["players"][1]
    assert view["staging"][-1] == {"uid": inst.uid, "facedown": True}
    assert view["bot"]["crew"] == "soval" and view["bot"]["command"][0]["image"] == "soval-traits"
    assert view["hand"] is None


# ------------------------------------------------------------------ choices and cards aimed at the Bot

def test_choices_put_to_the_bot_are_answered_automatically():
    """A question for the Bot never reaches anyone: here, which Duty Officer to dismiss when over its limit."""
    s = solo()
    bot = the_bot(s)
    bot.duty += [s.new_inst(c) for c in ("2PER07", "2PER11", "2PER14", "2PER10", "2PER13")]
    s.decision = None
    advance(s, flag_irreversible=False)
    # The Bot has one slot (REQ-SOLO-92), and each "dismiss one" was answered with the first option (REQ-SOLO-112).
    assert s.decision.seat == 0 and [i.card for i in the_bot(s).duty] == ["2PER13"]  # objects rebuilt on resume



def test_incidents_given_to_the_bot_go_on_its_deck():
    s = solo()
    bot = the_bot(s)
    acts = Actions(Ctx(s, OpRef(mode="auto", seat=0)), [A.TAKE_INCIDENT])
    taken = list(acts.take_incident(opponent=True))
    assert not bot.hand and CARDS[bot.draw[0].card].suit == "Incident"
    _ = taken


def test_bot_never_reacts():
    s = solo()
    bot = the_bot(s)
    bot.duty.append(s.new_inst("2SOV12"))  # V'Lar: a REACTION after putting an Ally into play
    from engine.ops import raise_event

    raise_event(s, "put_into_play", 1, bot.duty[0].uid)
    advance(s, flag_irreversible=False)
    assert s.decision.seat == 0 and s.offer is None


# ------------------------------------------------------------------ scoring and the end (REQ-SOLO-70 to -73)

def test_bot_scoring():
    s = solo()
    bot = the_bot(s)
    bot.dilithium, bot.latinum = 3, 2
    endgames = sum(1 for i in [bot.captain, *bot.draw, *bot.discard]
                   for op in CARDS[i.card].operations if op.kind == "ENDGAME")
    parts = score_player(s, bot)["parts"]
    assert parts["endgame"] == 5 * endgames and parts["resources"] == 2 and parts["missions"] == 0


def test_bot_scores_focus_without_missions():
    s = solo()
    bot = the_bot(s)
    bot.discard.append(s.new_inst("2PER16"))  # Riva: Influence Focus
    bot.highest["influence"] = 10
    assert not bot.missions_completed and score_player(s, bot)["parts"]["focus_influence"] > 0


def test_a_tie_is_a_loss():
    s = solo()
    human, bot = me(s), the_bot(s)
    human.glory = 0
    gap = score_player(s, bot)["total"] - score_player(s, human)["total"]
    human.glory += gap
    assert score_player(s, human)["total"] == score_player(s, bot)["total"]
    assert score_game(s)["winners"] == [bot.seat]
    human.glory += 1
    assert score_game(s)["winners"] == [human.seat]


def test_the_burn_is_a_loss():
    from engine.game import burn

    s = solo()
    burn(s)
    assert s.result["winners"] == [1]


def test_game_ends_with_a_bot_turn():
    from engine.game import trigger_resolution

    s = solo()
    trigger_resolution(s)  # during the human's turn 1
    assert s.last_turn % 2 == 1  # a Bot turn


def test_random_solo_games_finish():
    import random

    for seed in range(4):
        rng = random.Random(seed)
        s = solo(deck=rng.choice(["georgiou", "kirk", "pike"]), bot=rng.choice(["soval", "riker", "rebner"]),
                 difficulty=rng.choice(["ensign", "admiral"]), seed=seed)
        for _ in range(3000):
            if s.step == "over":
                break
            ids = [o.id for o in s.decision.options]
            assert s.decision.seat == 0
            plays = [i for i in ids if i.startswith(("play:", "activate:"))]
            choose(s, 0, rng.choice(plays) if plays and rng.random() < 0.85 else rng.choice(ids),
                   flag_irreversible=False)
        assert s.step == "over" and s.result
