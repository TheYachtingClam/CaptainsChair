"""Solo mode final sweep (plans/solo-mode.md Step 9): random games against every Bot at every difficulty, random
campaign games with every challenge and Boost, and undo around the Bot's turn (REQ-SOLO-200, -201)."""

import random

import pytest

from engine import upgrades
from engine.campaign import CHALLENGES, game_setup
from engine.game import advance, choose
from engine.setup import BOT_UNAVAILABLE, DIFFICULTIES, BotSetup, SeatSetup, new_game
from engine.content import content
from engine.views import game_view

BOTS = sorted(c for c in content().command if c not in BOT_UNAVAILABLE)
DECKS = ["georgiou", "soval", "kirk", "archer", "pike", "riker", "freeman", "rebner"]
upgrades.load()


def play_out(s, rng, limit=4000):
    """Random play for the human; the Bot plays itself. Returns the finished state."""
    advance(s, flag_irreversible=False)
    for n in range(limit):
        if s.step == "over":
            return s
        assert s.decision.seat == 0, s.decision.prompt  # the Bot never waits for an answer
        ids = [o.id for o in s.decision.options]
        plays = [i for i in ids if i.startswith(("play:", "activate:", "mission:"))]
        choose(s, 0, rng.choice(plays) if plays and rng.random() < 0.85 else rng.choice(ids), flag_irreversible=False)
        if n % 40 == 0:
            game_view(s, 0)  # views never fail mid-game
    raise AssertionError("the game did not finish")


@pytest.mark.parametrize("bot", BOTS)
@pytest.mark.parametrize("difficulty", DIFFICULTIES)
def test_random_game_against_every_bot_at_every_difficulty(bot, difficulty):
    seed = BOTS.index(bot) * 10 + DIFFICULTIES.index(difficulty)
    rng = random.Random(seed)
    s = new_game(seed, "solo", [SeatSetup("Me", rng.choice(DECKS), rng.choice(["basic", "advanced"]))],
                 ["second_contact"], True, bot=BotSetup(bot, difficulty, ticking_clock=seed % 3 == 0))
    s = play_out(s, rng)
    assert s.result and s.result["winners"] in ([0], [1])  # solo games always have a winner


@pytest.mark.parametrize("seed", range(6))
def test_random_campaign_games_with_challenges_and_boosts(seed):
    rng = random.Random(seed)
    deck = rng.choice(DECKS)
    outcomes = rng.choice([[], ["win"], ["win", "win"], ["win", "loss"]])
    boosts = rng.sample(sorted(upgrades.BOOSTS), 4)
    camp = game_setup(rng.choice(["ensign", "captain"]), outcomes, list(CHALLENGES), boosts, rng.choice(["dilithium", "latinum"]))
    pile = tuple(rng.sample(["2PER16", "2PER07"], rng.randint(0, 2)))
    s = new_game(seed, "solo", [SeatSetup("Me", deck, "basic", pile, camp)], ["second_contact"], False,
                 bot=BotSetup(rng.choice(BOTS), "commander"))
    s = play_out(s, rng)
    assert s.result


# ------------------------------------------------------------------ undo (REQ-SOLO-200, -201)

def test_undo_works_in_your_turn_but_not_across_the_bot_turn(authed):
    r = authed.post("/api/games", json={"display_name": "Me", "deck_id": "kirk", "mode": "solo",
                                        "bot": {"deck_id": "soval", "difficulty": "ensign"}})
    grant = r.json()
    game_id, h = grant["game"]["id"], {"X-Seat-Token": grant["seat_token"]}
    cmd = lambda option: authed.post(f"/api/games/{game_id}/commands", json={"option": option}, headers=h)  # noqa: E731

    view = cmd("end").json()  # end the Action Step: nothing revealed yet
    assert view["can_undo"]
    view = authed.post(f"/api/games/{game_id}/undo", headers=h).json()
    assert view["decision"]["kind"] == "action"

    # Ending the turn is flagged first, because the Bot's turn follows and reveals cards.
    view = cmd("end").json()
    last = None
    for _ in range(20):
        if view["decision"]["kind"] == "action" and view["turn"] > 0:
            break
        last = next((o for o in view["decision"]["options"] if o["id"] == "done"), view["decision"]["options"][0])
        view = cmd(last["id"]).json()
    # The move that handed the turn to the Bot carried the can't-be-undone warning (REQ-SOLO-200).
    assert last is not None and last["irreversible"]
    assert view["turn"] >= 2 and view["active"] == 0  # the Bot has had its turn and it is ours again
    assert view["bot_turn"]["steps"]
    assert not view["can_undo"]
    assert authed.post(f"/api/games/{game_id}/undo", headers=h).status_code == 409
