#!/usr/bin/env python3
"""Rebuild the game of a bug report and print where it stands.

    scripts/replay_bug.py report.json              # the state when the bug was reported
    scripts/replay_bug.py report.json --moves 40   # the state after the first 40 commands
    scripts/replay_bug.py report.json --back 3     # three commands before the report
    scripts/replay_bug.py report.json --state out.json   # also write the whole engine state

report.json is the file the Admin page downloads for a report (GET /api/admin/bugs/{id}). The game is replayed from
its seed and commands with the rules as they are in this checkout, so a fixed bug shows as a changed outcome.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

SERVER = Path(__file__).resolve().parent.parent / "server"
sys.path.insert(0, str(SERVER))
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("report", type=Path)
    parser.add_argument("--moves", type=int, help="keep only the first N commands")
    parser.add_argument("--back", type=int, help="drop the last N commands")
    parser.add_argument("--log", type=int, default=25, help="how many log lines to print (default 25)")
    parser.add_argument("--state", type=Path, help="write the engine state as JSON to this file")
    args = parser.parse_args()

    from app import bugs

    report = json.loads(args.report.read_text())
    data = report.get("bundle", report)
    total = len(data["commands"])
    moves = args.moves if args.moves is not None else (total - args.back if args.back else None)
    state = bugs.rebuild(data, moves=moves)

    game = data["game"]
    print(f"Bug report {report.get('id', '(bundle only)')}  {report.get('created_at', '')}")
    if report.get("description"):
        print(f"  {report.get('reporter', '?')} (seat {report.get('seat', '?')}): {report['description']}")
    seats = ", ".join(f"{s['display_name']} ({s['deck_id']}, {s['board_side']})" for s in game["seats"])
    print(f"Game {game['id']}: {game['mode']}, box {game.get('box')}, seed {game['seed']}; {seats}"
          + (f"; Bot {game['bot']['deck_id']} ({game['bot'].get('difficulty')})" if game.get("bot") else ""))
    print(f"Replayed {total if moves is None else moves} of {total} commands "
          f"(reported at turn {data.get('turn')}, step {data.get('step')}).")
    print(f"Now: turn {state.turn}, step {state.step}, active seat {state.active}.")
    print(f"\nLast {args.log} log lines:")
    for event in state.log[-args.log:]:
        print(f"  {event.text}")
    if state.decision is not None:
        d = state.decision
        print(f"\nWaiting for seat {d.seat} ({d.kind}): {d.prompt}")
        for o in d.options:
            print(f"  [{o.id}] {o.label}")
    else:
        print("\nNo decision is pending." + (f" Result: {state.result}" if state.result else ""))
    if args.state:
        args.state.write_text(state.model_dump_json(indent=1))
        print(f"\nState written to {args.state}")


if __name__ == "__main__":
    main()
