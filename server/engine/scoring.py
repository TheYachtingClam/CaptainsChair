"""Final scoring (requirements/13-final-scoring.md) and the Burn count."""

from __future__ import annotations

from engine import cards as registry
from engine.content import content
from engine.state import SPECIALTIES, GameState, Inst, Player


def _with_beamed(cards: list[Inst]) -> list[Inst]:
    out = []
    for inst in cards:
        out.append(inst)
        out.extend(_with_beamed(inst.beamed))
    return out


def owned_cards(player: Player) -> list[Inst]:
    """Every card the player owns that counts at final scoring: not Reserve or Development (REQ-FS-02)."""
    zones = [player.hand, player.draw, player.discard, player.staging, player.fleet, player.locations,
             player.duty, player.log, player.status, [player.captain]]
    return _with_beamed([inst for zone in zones for inst in zone])


def _table(player: Player) -> list[Inst]:
    return [player.captain, *player.status, *player.fleet, *player.locations, *player.duty]


def incidents_owned(player: Player) -> int:
    """Incidents for the Burn: hand, play, Discard pile, Draw deck and Log; not the Reserve (REQ-OV-23)."""
    cards = content().cards
    return sum(1 for inst in owned_cards(player) if cards[inst.card].suit == "Incident")


def printed_vp(value) -> int:
    """Printed VP as a number. "?" (set by a Focus icon) and asterisk rules count 0 here."""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        digits = value.rstrip("*")
        if digits.lstrip("-").isdigit():
            return int(digits)
    return 0


def score_player(state: GameState, player: Player) -> dict:
    data = content()
    board = data.boards[player.board]
    cards = [data.cards[i.card] for i in owned_cards(player)]
    multipliers = {s: board.multiplier(s, player.highest[s]) for s in SPECIALTIES}
    neutral_tokens = sum(loc.away.get(player.seat, 0) for loc in state.neutral) + sum(
        1 for ship in player.fleet if ship.at in {loc.uid for loc in state.neutral})

    focus = {s: 0 for s in SPECIALTIES}
    best = 0
    if player.missions_completed:  # REQ-MS-08
        for c in cards:
            if c.focus == "Best":
                best += max(multipliers.values(), default=0)
            elif c.focus and c.focus.lower() in focus:
                focus[c.focus.lower()] += multipliers[c.focus.lower()]
    missions = sum(m.vp or 0 for m in board.missions if m.id in player.missions_completed) if board.side == "advanced" else 0

    parts = {
        "glory": player.glory,
        "neutral_tokens": neutral_tokens,
        "endgame": sum(registry.ENDGAME[i.card](state, player) for i in _table(player) if i.card in registry.ENDGAME),
        "printed_vp": sum(printed_vp(c.vp) for c in cards),
        "focus_research": focus["research"],
        "focus_influence": focus["influence"],
        "focus_military": focus["military"],
        "focus_best": best,
        "missions": missions,
    }
    return {"seat": player.seat, "name": player.name, "parts": parts, "total": sum(parts.values())}


def score_game(state: GameState) -> dict:
    scores = [score_player(state, p) for p in state.players]
    top = max(s["total"] for s in scores)
    return {"scores": scores, "winners": [s["seat"] for s in scores if s["total"] == top]}  # a tie means both win
