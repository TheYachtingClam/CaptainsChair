#!/usr/bin/env python3
"""How many printed card operations have code, by group (plans/card-implementation.md), plus the solo Bot's
Automated Command rows and the Five-Year Mission bonuses (plans/solo-mode.md).

Usage:
  scripts/card_coverage.py              the summary table
  scripts/card_coverage.py --missing    also list every operation still without code, by group
  scripts/card_coverage.py --group Ship  only groups whose name contains this text

PASSIVE and ENDGAME operations count as done when the card has a registered modifier, trigger or
ENDGAME function. Stardate WHEN EMPTIED and STARDATE RESOLUTION are run by the engine, so they are
not listed, and neither are the "Surprise" rows of the Bot's TRAITS side, which run the card's own SURPRISE.
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


SOLO = "Solo only (needs the Bot)"


def group_of(card) -> str:
    if (card.position or "").startswith("Solo"):
        return SOLO
    if card.suit == "Stardate":
        return "Stardates"
    if card.position == "Rewards":
        return f"Reward pile ({card.set})"
    if card.is_common:
        kind = "Market" if card.suit in MARKET_SUITS else card.suit
        return f"{kind} ({card.set})"
    return f"Crew: {card.deck}"


def has_code(card_id: str, index: int, kind: str) -> bool:
    return registry.has_code(card_id, index, kind)


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
            if op.kind == "SURPRISE" and group != SOLO:  # Bot-only operations on ordinary cards
                solo = rows.setdefault(SOLO, [0, 0, 0, []])
                solo[1] += 1
                solo[2] += has_code(card.id, index, op.kind)
                if not has_code(card.id, index, op.kind):
                    solo[3].append(f"{card.id} {card.name}: {index} {op.kind}")
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
    if not only or "bot" in only or "bonus" in only or "mission" in only:
        _solo_rows(rows)
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


def _solo_rows(rows: dict[str, list]) -> None:
    """One group per Bot Crew for its Automated Command rows, and one for every Five-Year Mission bonus."""
    from engine import bot, upgrades

    upgrades.load()
    for crew_id, crew in sorted(content().command.items()):
        row = rows.setdefault(f"Bot rows: {crew_id}", [0, 0, 0, []])
        for side in crew.sides:
            row[0] += 1
            for r in side.rows:
                if "Surprise" in r.matches:
                    continue
                row[1] += 1
                if (crew_id, side.side, r.number) in bot.ROWS:
                    row[2] += 1
                else:
                    row[3].append(f"{side.side} row {r.number}: {', '.join(r.matches)}")
        bonuses = rows.setdefault("Five-Year Mission bonuses", [0, 0, 0, []])
        bonuses[0] += 1
        for side, section in (("win", crew.upgrades.win), ("loss", crew.upgrades.loss)):
            for i, printed in enumerate(section.bonuses):
                key = upgrades.key(crew_id, side, i)
                bonuses[1] += 1
                if key in upgrades.BOOSTS or key in upgrades.REINFORCES:
                    bonuses[2] += 1
                else:
                    bonuses[3].append(f"{key}: {printed}")


if __name__ == "__main__":
    sys.exit(main())
