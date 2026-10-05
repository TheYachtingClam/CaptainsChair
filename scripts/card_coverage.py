#!/usr/bin/env python3
"""How many printed card operations have code, by group (plans/card-implementation.md).

Usage:
  scripts/card_coverage.py              the summary table
  scripts/card_coverage.py --missing    also list every operation still without code, by group
  scripts/card_coverage.py --group Ship  only groups whose name contains this text

PASSIVE and ENDGAME operations count as done when the card has a registered modifier, trigger or
ENDGAME function. Stardate WHEN EMPTIED and STARDATE RESOLUTION are run by the engine, so they are
not listed.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

SERVER = Path(__file__).resolve().parent.parent / "server"

try:
    sys.path.insert(0, str(SERVER))
    os.chdir(SERVER)
    from engine import cards as registry
    from engine.content import MARKET_SUITS, content
except ImportError:  # not inside the server environment: re-run there
    os.execvp("uv", ["uv", "run", "--project", str(SERVER), "python", __file__, *sys.argv[1:]])

ENGINE_KINDS = {"WHEN EMPTIED", "STARDATE RESOLUTION"}


def group_of(card) -> str:
    if card.suit == "Stardate":
        return "Stardates"
    if card.position == "Rewards":
        return f"Reward pile ({card.set})"
    if card.is_common:
        kind = "Market" if card.suit in MARKET_SUITS else card.suit
        return f"{kind} ({card.set})"
    return f"Crew: {card.deck}"


def has_code(card_id: str, index: int, kind: str) -> bool:
    if (card_id, index) in registry.OPS:
        return True
    if kind == "DEVELOPMENT COST":
        return card_id in registry.DEV_COSTS
    if kind == "ENDGAME":
        return card_id in registry.ENDGAME
    if kind in ("PASSIVE", "SPECIAL"):
        return any(card_id in reg for reg in (registry.HAND_SIZE, registry.DUTY_LIMIT, registry.SKILLS,
                                              registry.SCANS_INCLUDE_JUNK, registry.STATE_CHECKS,
                                              registry.DISMISS_REWARDS, registry.NO_OPPONENT_REACTIONS,
                                              registry.DUTY_SLOTS, registry.RESTRICTIONS, registry.TRAIT_MODIFIERS))
    return False


def main() -> int:
    args = sys.argv[1:]
    only = args[args.index("--group") + 1].lower() if "--group" in args else ""
    rows: dict[str, list] = {}
    for card in sorted(content().cards.values(), key=lambda c: c.id):
        group = group_of(card)
        if only and only not in group.lower():
            continue
        row = rows.setdefault(group, [0, 0, 0, []])
        row[0] += 1
        for index, op in enumerate(card.operations):
            if op.kind in ENGINE_KINDS:
                continue
            row[1] += 1
            if has_code(card.id, index, op.kind):
                row[2] += 1
            else:
                row[3].append(f"{card.id} {card.name}: {index} {op.kind}")
    if not only or only in "crew board missions":
        seen: set[str] = set()
        row = rows.setdefault("Crew board missions", [0, 0, 0, []])
        for board in sorted(content().boards.values(), key=lambda b: b.id):
            for mission in board.missions:
                if mission.id in seen:
                    continue  # the same mission on both sides of a board
                seen.add(mission.id)
                row[0] += 1
                row[1] += 1
                impl = registry.MISSIONS.get(mission.id)
                if impl and impl.goal and impl.reward:
                    row[2] += 1
                else:
                    row[3].append(f"{board.captain}: {mission.name}")
    width = max(len(g) for g in rows) if rows else 10
    print(f"{'Group':<{width}}  Cards  Operations with code")
    total = [0, 0]
    for group in sorted(rows):
        cards, ops, done, _ = rows[group]
        total[0] += ops
        total[1] += done
        print(f"{group:<{width}}  {cards:>5}  {done:>4} of {ops:<4} {'done' if ops and done == ops else ''}")
    print(f"{'All':<{width}}         {total[1]:>4} of {total[0]}")
    if "--missing" in args:
        for group in sorted(rows):
            if rows[group][3]:
                print(f"\n{group}:")
                for line in rows[group][3]:
                    print(f"  {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
