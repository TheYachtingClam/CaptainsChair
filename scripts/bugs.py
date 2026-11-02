#!/usr/bin/env python3
"""Fetch bug reports from the live server and mark them resolved, with the bug token (REQ-BUG-10).

    scripts/bugs.py list                 open reports, newest first
    scripts/bugs.py list --all           resolved ones too
    scripts/bugs.py get 3f2a             download a report to bugs/bug-<id>.json (a unique prefix of the id is enough)
    scripts/bugs.py get newest           the newest open bug (not a feature request)
    scripts/bugs.py fixture 3f2a         write the trimmed bundle to server/tests/bugs/<prefix>.json for a test
    scripts/bugs.py resolve 3f2a [...]   mark reports resolved (the deploy workflow does this)

It reads CC_URL (the site, e.g. https://captains-chair-wild-bush-4325.fly.dev) and CC_BUG_TOKEN (the server's
BUG_API_TOKEN). The file `get` writes is the Admin page's download, so scripts/replay_bug.py reads it unchanged.
Standard library only, so it runs anywhere, including the deploy workflow. See plans/bug-pipeline.md.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent
DOWNLOADS = ROOT / "bugs"
FIXTURES = ROOT / "server" / "tests" / "bugs"
FIXTURE_ID_LENGTH = 8

# (method, path, JSON body or None) -> (status code, response body)
Transport = Callable[[str, str, "dict | None"], "tuple[int, bytes]"]


class BugError(Exception):
    """A problem to report to the user, without a traceback."""


def http_transport(base_url: str, token: str) -> Transport:
    """Requests to the live server, with the token as a bearer header."""
    base = base_url.rstrip("/")

    def send(method: str, path: str, body: dict | None) -> tuple[int, bytes]:
        data = None if body is None else json.dumps(body).encode()
        request = urllib.request.Request(base + path, data=data, method=method)
        request.add_header("Authorization", f"Bearer {token}")
        request.add_header("Accept", "application/json")
        if data is not None:
            request.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as error:
            return error.code, error.read()
        except urllib.error.URLError as error:
            raise BugError(f"Cannot reach {base}: {error.reason}. Is the host allowed in the network settings?")

    return send


class Bugs:
    def __init__(self, transport: Transport) -> None:
        self.send = transport

    def _call(self, method: str, path: str, body: dict | None = None) -> bytes:
        code, payload = self.send(method, path, body)
        if code == 401:
            raise BugError("The server refused the token: check CC_BUG_TOKEN against the server's BUG_API_TOKEN.")
        if code == 404:
            raise BugError(f"Not found: {path}")
        if code >= 400:
            raise BugError(f"{method} {path} failed with {code}: {payload[:300]!r}")
        return payload

    def reports(self, *, include_resolved: bool = False) -> list[dict]:
        listed = json.loads(self._call("GET", "/api/admin/bugs"))
        return listed if include_resolved else [r for r in listed if r.get("status") == "open"]

    def resolve_id(self, ref: str) -> str:
        """The full id for `ref`: a full id, a unique prefix, or `newest` (the newest open bug)."""
        listed = self.reports(include_resolved=True)
        if ref == "newest":
            bugs = [r for r in listed if r.get("status") == "open" and r.get("kind", "bug") == "bug"]
            if not bugs:
                raise BugError("There are no open bug reports.")
            return bugs[0]["id"]  # the server lists newest first
        matches = [r["id"] for r in listed if r["id"].startswith(ref)]
        if not matches:
            raise BugError(f"No report id starts with {ref!r}.")
        if len(matches) > 1:
            raise BugError(f"{ref!r} matches {len(matches)} reports; give more of the id.")
        return matches[0]

    def download(self, ref: str) -> tuple[str, bytes]:
        """The report file as the server writes it (REQ-BUG-06): no number passes through anything that rounds."""
        bug_id = self.resolve_id(ref)
        return bug_id, self._call("GET", f"/api/admin/bugs/{bug_id}/download")

    def set_status(self, ref: str, status: str) -> dict:
        bug_id = self.resolve_id(ref)
        return json.loads(self._call("POST", f"/api/admin/bugs/{bug_id}/status", {"status": status}))


def trim(report: dict) -> dict:
    """What a regression test needs from a report: the setup, the seed and the commands, with the players' names
    replaced and their views and log lines left out (plans/bug-pipeline.md, Decision 4)."""
    bundle = report.get("bundle", report)
    game = dict(bundle["game"])
    game["seats"] = [{**seat, "display_name": f"Player {seat['index'] + 1}"} for seat in game["seats"]]
    game.pop("id", None)
    return {
        "id": report.get("id"),
        "kind": report.get("kind", "bug"),
        "description": report.get("description", ""),
        "bundle": {
            "version": bundle.get("version"),
            "game": game,
            "commands": bundle["commands"],
            "reporter_seat": bundle.get("reporter_seat", report.get("seat")),
            "turn": bundle.get("turn"),
            "step": bundle.get("step"),
        },
    }


def _line(r: dict) -> str:
    crews = ", ".join(r.get("players") or [])
    if r.get("bot"):
        crews += f" vs Bot {r['bot']}"
    text = " ".join((r.get("description") or "").split())
    if len(text) > 100:
        text = text[:97] + "..."
    return (f"{r['id'][:8]}  {r.get('kind', 'bug'):7} {r.get('status', ''):8} {(r.get('created_at') or '')[:16]:16}  "
            f"{r.get('mode') or '?'}, {r.get('box') or '?'}, {crews}; turn {r.get('turn')}, {r.get('moves')} moves\n"
            f"          {text}")


def run(argv: list[str], transport: Transport | None = None, out=sys.stdout,
        downloads: Path = DOWNLOADS, fixtures: Path = FIXTURES) -> int:
    parser = argparse.ArgumentParser(prog="scripts/bugs.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    listing = sub.add_parser("list", help="list open reports, newest first")
    listing.add_argument("--all", action="store_true", help="include resolved reports")
    sub.add_parser("get", help="download a report").add_argument("ref")
    sub.add_parser("fixture", help="write a trimmed report for a regression test").add_argument("ref")
    sub.add_parser("resolve", help="mark reports resolved").add_argument("refs", nargs="+")
    sub.add_parser("reopen", help="mark reports open again").add_argument("refs", nargs="+")
    args = parser.parse_args(argv)

    if transport is None:
        url, token = os.environ.get("CC_URL", ""), os.environ.get("CC_BUG_TOKEN", "")
        if not url or not token:
            print("Set CC_URL and CC_BUG_TOKEN (see plans/bug-pipeline.md).", file=sys.stderr)
            return 2
        transport = http_transport(url, token)
    bugs = Bugs(transport)

    try:
        if args.command == "list":
            listed = bugs.reports(include_resolved=args.all)
            for r in listed:
                print(_line(r), file=out)
            if not listed:
                print("No open reports." if not args.all else "No reports.", file=out)
        elif args.command == "get":
            bug_id, body = bugs.download(args.ref)
            downloads.mkdir(parents=True, exist_ok=True)
            path = downloads / f"bug-{bug_id}.json"
            path.write_bytes(body)
            report = json.loads(body)
            print(f"Saved {path}", file=out)
            print(_line(report), file=out)
            print(f"Replay it with: scripts/replay_bug.py {path}", file=out)
        elif args.command == "fixture":
            bug_id, body = bugs.download(args.ref)
            fixtures.mkdir(parents=True, exist_ok=True)
            path = fixtures / f"{bug_id[:FIXTURE_ID_LENGTH]}.json"
            path.write_text(json.dumps(trim(json.loads(body)), indent=1) + "\n")
            print(f"Saved {path}", file=out)
        else:
            status = "resolved" if args.command == "resolve" else "open"
            for ref in args.refs:
                r = bugs.set_status(ref, status)
                print(f"{r['id'][:8]} is {r['status']}", file=out)
    except BugError as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
