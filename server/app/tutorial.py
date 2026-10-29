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
    found = [yaml.safe_load(path.read_text()) for path in sorted(SCRIPTS.glob("*.yaml"))]
    found.sort(key=lambda script: script.get("order", 99))  # the lobby's order: the first tutorial comes first
    return {script["id"]: script for script in found}


GUIDES = SCRIPTS.parent / "guides"


@lru_cache
def guide(guide_id: str) -> dict:
    """A reference sheet the coach opens with "?" (REQ-TUT-43), such as How cards work."""
    path = GUIDES / f"{guide_id}.yaml"
    if not guide_id.replace("-", "").isalnum() or not path.is_file():
        raise TutorialError(f"No guide {guide_id!r}")
    return yaml.safe_load(path.read_text())


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
    if kind == "react":  # a Reaction offered as "<uid>:<n>"
        card_id, _, n = rest.rpartition(":")
        return next((o.id for o in options if o.id.partition(":")[2] == n and by_uid.get(o.id.partition(":")[0])
                     and by_uid[o.id.partition(":")[0]].card == card_id), None)
    if kind == "pick":
        return next((o.id for o in options if o.id in by_uid and cards[by_uid[o.id].card].suit == rest), None)
    if rest in cards:  # "<prefix>:<card id>", such as take:1LOC19 or discard:1PIC16
        return next((o.id for o in options if o.id.startswith(f"{kind}:") and by_uid.get(o.id[len(kind) + 1:])
                     and by_uid[o.id[len(kind) + 1:]].card == rest), None)
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
    out = {"id": data["id"], "title": data["title"], "index": index, "total": len(steps), "free": free, "step": None,
           "tip": tip(game, state)}
    if not free:
        step = steps[index]
        out["step"] = {"id": step["id"], "say": step["say"].strip(), "more": (step.get("more") or "").strip() or None,
                       "show": step.get("show"), "next": not _wants(step)}
    return out


# ----------------------------------------------------------------------------- tips (REQ-TUT-30, -31)

# A `question` trigger names the kind of question by words in its prompt; "mission" is a mission that can be claimed.
QUESTION_WORDS = {"encounter": "encounter", "develop": "development"}


def _triggered(when: dict, state: GameState) -> bool:
    me = state.players[0]
    decision = state.decision
    mine = decision is not None and decision.seat == 0
    if "question" in when:
        kind = when["question"]
        if kind == "mission":
            return mine and any(o.id.startswith("mission:") for o in decision.options)
        return mine and QUESTION_WORDS.get(kind, kind) in decision.prompt.lower()
    if "playable" in when:
        return mine and any(resolve(state, f"play:{when['playable']}:{n}") for n in range(4))
    if "track_at_least" in when:
        return any(v >= when["track_at_least"] for v in me.tracks.values())
    if "event" in when:
        if when["event"] == "take_incident":  # an Incident in your hand
            return any(content().cards[i.card].suit == "Incident" for i in me.hand)
        return False
    moment = when.get("moment")
    if moment == "stardate-empties":  # the first Stardate card is used up: 2 in Cadet Training, 3 against a Bot
        return len(state.stardates) < (3 if state.mode == "solo" else 2) and state.result is None
    if moment == "last-turn":
        return state.last_turn is not None and state.turn >= state.last_turn and state.result is None
    if moment in ("final-scoring", "game-over"):
        return state.result is not None
    return False


def tip(game: Game, state: GameState) -> dict | None:
    """The tip to show now: the first one, in the script's order, whose trigger holds and that has not been closed.
    Tips appear only once the guided part is over (REQ-TUT-31)."""
    if not game.tutorial or not progress(game)[1]:
        return None
    closed = {str(c["option"])[len("tutorial:tip:"):] for c in game.commands
              if not c.get("undone") and str(c.get("option", "")).startswith("tutorial:tip:")}
    for t in script(game.tutorial["id"]).get("tips", []):
        if t["id"] not in closed and _triggered(t.get("when", {}), state):
            return {"id": t["id"], "say": t["say"].strip(), "show": t.get("show"), "link": t.get("link")}
    return None
