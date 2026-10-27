"""Tutorials (requirements/24-tutorials.md): a script of steps that coaches a real game. The engine knows nothing of
them; this module works out the current step from the game's moves, keeps the player on the script's rails, and adds
the coach's text to the view."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from app.models import Game
from engine.content import content
from engine.state import GameState

SCRIPTS = Path(__file__).resolve().parent.parent / "content" / "tutorials"


class TutorialError(Exception):
    pass


@lru_cache
def scripts() -> dict[str, dict]:
    """Every tutorial script, by id (REQ-TUT-01)."""
    out = {}
    for path in sorted(SCRIPTS.glob("*.yaml")):
        script = yaml.safe_load(path.read_text())
        out[script["id"]] = script
    return out


def script(tutorial_id: str) -> dict:
    found = scripts().get(tutorial_id)
    if found is None:
        raise TutorialError(f"No tutorial {tutorial_id!r}")
    return found


def _wants(step: dict) -> list[str]:
    want = step.get("expect")
    return [] if want is None else [str(w) for w in (want if isinstance(want, list) else [want])]


def progress(game: Game) -> tuple[int, bool]:
    """The current step's index and whether the rails have ended (REQ-TUT-24, -25). Each Next taps past an
    explanation, each move answers the step that expected it; Let me play, or running out of steps, ends the rails."""
    steps = script(game.tutorial["id"])["steps"]
    index, free = 0, False
    for command in game.commands:
        if command.get("undone") or command.get("dropped") or "note" in command:
            continue
        option = str(command.get("option", ""))
        if option == "tutorial:free":
            free = True
        elif option == "tutorial:next":
            index += 1
        elif not free and index < len(steps) and _wants(steps[index]):
            index += 1
    return index, free or index >= len(steps)


# ----------------------------------------------------------------------------- translating `expect`


def _instances(state: GameState) -> dict:
    """Every card instance on the table, in decks and in the Market, by uid."""
    found = []
    for p in state.players:
        for zone in ("hand", "draw", "discard", "reserve", "development", "staging", "fleet", "locations", "duty",
                     "log", "status"):
            for i in getattr(p, zone):
                found += [i, *getattr(i, "beamed", [])]
        found.append(p.captain)
    found += [i for i in state.market.values() if i] + [i for d in state.market_decks.values() for i in d]
    found += state.neutral + state.location_deck + state.incident + state.junk + state.encounter
    return {i.uid: i for i in found}


def resolve(state: GameState, want: str) -> str | None:
    """The answer to the current question that a script's `expect` names (REQ-TUT-22), or None."""
    options = state.decision.options if state.decision else []
    ids = [o.id for o in options]
    if want in ids:
        return want
    cards = content().cards
    by_uid = _instances(state)
    kind, _, rest = want.partition(":")
    if kind in ("play", "activate"):
        card_id, _, n = rest.rpartition(":")
        for o in options:
            k, uid, m = (o.id.split(":") + ["", ""])[:3]
            if k == kind and m == n and uid in by_uid and by_uid[uid].card == card_id:
                return o.id
        return None
    if kind == "take":
        return next((o.id for o in options if o.id.startswith("take:") and by_uid.get(o.id[5:])
                     and by_uid[o.id[5:]].card == rest), None)
    if kind == "pick":
        return next((o.id for o in options if o.id in by_uid and cards[by_uid[o.id].card].suit == rest), None)
    return next((o.id for o in options if o.id in by_uid and by_uid[o.id].card == want), None)


# ----------------------------------------------------------------------------- the rails


def allowed(game: Game, state: GameState) -> set[str] | None:
    """The answers the player may give now: None when the rails are off (anything goes), otherwise the step's
    expected answers, or none at all while an explanation waits for Next (REQ-TUT-23)."""
    if not game.tutorial:
        return None
    index, free = progress(game)
    if free:
        return None
    step = script(game.tutorial["id"])["steps"][index]
    return {got for want in _wants(step) if (got := resolve(state, want))}


def check(game: Game, state: GameState, option: str) -> None:
    """Refuse a move the coach is not waiting for (REQ-TUT-23)."""
    ok = allowed(game, state)
    if ok is not None and option not in ok:
        index, _ = progress(game)
        step = script(game.tutorial["id"])["steps"][index]
        raise TutorialError("Tap Next to continue the tutorial" if not _wants(step)
                            else "The tutorial is waiting for another move: follow the coach, or choose Let me play")


def block(game: Game, state: GameState) -> dict | None:
    """The coach's part of the view (REQ-TUT-40)."""
    if not game.tutorial:
        return None
    data = script(game.tutorial["id"])
    steps = data["steps"]
    index, free = progress(game)
    out = {"id": data["id"], "title": data["title"], "index": index, "total": len(steps), "free": free, "step": None}
    if not free:
        step = steps[index]
        out["step"] = {"id": step["id"], "say": step["say"].strip(), "show": step.get("show"),
                       "next": not _wants(step)}
    return out
