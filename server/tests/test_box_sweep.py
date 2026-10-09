"""The final sweep of plans/base-game.md (Step 15): random games for every Crew and every Bot with each box choice,
in two-player, Cadet Training, solo and campaign games. A game must finish and never raise."""

import random

import pytest

from engine import upgrades
from engine.campaign import CHALLENGES, game_setup
from engine.game import advance, choose
from engine.setup import BOXES, BotSetup, SeatSetup, new_game
from engine.views import game_view

upgrades.load()

CREWS = {
    "base_game": ["picard", "shran", "koloth", "sela", "sisko", "burnham"],
    "to_boldly_go": ["georgiou", "soval", "kirk", "archer", "rebner", "khan"],
    "second_contact": ["pike", "riker", "freeman"],
}
EXPANSIONS = ["second_contact"]


def crews(box):
    return [c for s in (*BOXES[box], *EXPANSIONS) for c in CREWS[s]]


def play_out(s, rng, limit=8000, human_only=False):
    advance(s, flag_irreversible=False)
    for n in range(limit):
        if s.step == "over":
            return s
        if human_only:
            assert s.decision.seat == 0, s.decision.prompt
        ids = [o.id for o in s.decision.options]
        plays = [i for i in ids if i.startswith(("play:", "activate:", "mission:"))]
        choose(s, s.decision.seat, rng.choice(plays) if plays and rng.random() < 0.85 else rng.choice(ids),
               flag_irreversible=False)
        if n % 60 == 0:
            for seat in range(len(s.players)):
                game_view(s, seat)
    raise AssertionError("the game did not finish")


PAIRS = [(box, crew) for box in BOXES for crew in crews(box)]


@pytest.mark.parametrize("box,crew", PAIRS)
def test_two_player_game_with_every_crew_in_every_box(box, crew):
    pool = crews(box)
    seed = PAIRS.index((box, crew)) + 100
    other = pool[(pool.index(crew) + 1 + seed % (len(pool) - 1)) % len(pool)]
    other = other if other != crew else pool[(pool.index(crew) + 1) % len(pool)]
    s = new_game(seed, "two_player", [SeatSetup("P", crew, "advanced" if seed % 2 else "basic"),
                                      SeatSetup("O", other, "basic" if seed % 3 else "advanced")],
                 EXPANSIONS, seed % 2 == 0, box=box)
    assert play_out(s, random.Random(seed)).result


@pytest.mark.parametrize("box,crew", PAIRS)
def test_cadet_training_with_every_crew_in_every_box(box, crew):
    seed = PAIRS.index((box, crew)) + 300
    s = new_game(seed, "cadet", [SeatSetup("P", crew, "advanced" if seed % 2 else "basic")], EXPANSIONS,
                 seed % 2 == 1, box=box)
    assert play_out(s, random.Random(seed)).step == "over"


@pytest.mark.parametrize("box,bot", PAIRS)
def test_solo_game_against_every_bot_in_every_box(box, bot):
    pool = crews(box)
    seed = PAIRS.index((box, bot)) + 500
    rng = random.Random(seed)
    difficulty = ["ensign", "lieutenant", "commander", "captain", "admiral"][seed % 5]
    core = "base_game" in BOXES[box]
    s = new_game(seed, "solo", [SeatSetup("Me", rng.choice(pool), rng.choice(["basic", "advanced"]))], EXPANSIONS,
                 seed % 2 == 0, bot=BotSetup(bot, difficulty, ticking_clock=seed % 3 == 0,
                                             conspiracy=core and seed % 4 < 2), box=box)
    s = play_out(s, rng, human_only=True)
    assert s.result and s.result["winners"] in ([0], [1])


@pytest.mark.parametrize("seed", range(12))
def test_campaign_games_with_core_box_crews_bots_and_boosts(seed):
    rng = random.Random(seed + 900)
    box = ["core", "both"][seed % 2]
    pool = crews(box) if box == "both" else CREWS["base_game"]
    expansions = EXPANSIONS if box == "both" else []
    outcomes = rng.choice([[], ["win"], ["win", "win"], ["win", "loss"]])
    boosts = rng.sample(sorted(upgrades.BOOSTS), 4)
    camp = game_setup(rng.choice(["ensign", "captain"]), outcomes, list(CHALLENGES), boosts,
                      rng.choice(["dilithium", "latinum"]))
    pile = tuple(rng.sample(["1CAR04", "1PER15", "1SHI08"], rng.randint(0, 3)))
    s = new_game(seed, "solo", [SeatSetup("Me", rng.choice(pool), "basic", pile, camp)], expansions, False,
                 bot=BotSetup(rng.choice(pool), "commander"), box=box)
    assert play_out(s, rng, human_only=True).result
