"""Bug reports (requirements/19-technical-architecture.md §5.5): the bundle saved with a report, and rebuilding a
game from one. A game is its setup, its seed and its commands, so the bundle holds exactly those; the engine replays
them to give the same state, at the report or at any earlier move."""

from __future__ import annotations

import uuid

from app import play
from app.models import Game, Seat
from engine.state import GameState
from engine.views import game_view

VERSION = 1
RECENT_LOG = 60  # log lines kept for reading at a glance (REQ-BUG-04)


def bundle(game: Game, seat: int) -> dict:
    """Everything needed to recreate `game` as it is now, and what the reporter at `seat` was looking at."""
    state = play.build(game)
    decision = state.decision
    return {
        "version": VERSION,
        "game": {
            "id": game.id,
            "mode": game.mode,
            "box": game.box,
            "expansions": list(game.expansions or []),
            "promos": bool(game.promos),
            "promo_sets": None if game.promo_sets is None else list(game.promo_sets),
            "seed": game.seed,
            "bot": game.bot,
            "campaign": game.campaign,
            "status": game.status,
            "seats": [{"index": s.index, "display_name": s.display_name, "deck_id": s.deck_id,
                       "board_side": s.board_side} for s in sorted(game.seats, key=lambda s: s.index)],
        },
        "commands": [dict(c) for c in game.commands or []],
        "reporter_seat": seat,
        "turn": state.turn,
        "step": state.step,
        "active": state.active,
        "decision": None if decision is None else {
            "seat": decision.seat, "kind": decision.kind, "prompt": decision.prompt,
            "options": [{"id": o.id, "label": o.label} for o in decision.options]},
        "recent_log": [e.text for e in state.log[-RECENT_LOG:]],
        "view": game_view(state, seat),
    }


def as_game(data: dict, *, moves: int | None = None) -> Game:
    """A Game row built from a bundle, not yet in any database. `moves` keeps only the first that many commands, to
    look at an earlier moment (REQ-BUG-06)."""
    g = data["game"]
    commands = [dict(c) for c in data["commands"]]
    game = Game(id=str(uuid.uuid4()), mode=g["mode"], box=g.get("box", "to_boldly_go"), expansions=g["expansions"],
                promos=g["promos"], promo_sets=g.get("promo_sets"), seed=g["seed"], bot=g.get("bot"),
                campaign=g.get("campaign"), status=g.get("status", "active"),
                commands=commands if moves is None else commands[:moves])
    for s in g["seats"]:
        game.seats.append(Seat(index=s["index"], display_name=s["display_name"], deck_id=s["deck_id"],
                               board_side=s["board_side"], token_hash=""))
    return game


def rebuild(data: dict, *, moves: int | None = None) -> GameState:
    """The engine state a bundle describes, by replaying its commands with today's rules."""
    game = as_game(data, moves=moves)
    try:
        return play.build(game)
    finally:
        play.forget(game.id)
