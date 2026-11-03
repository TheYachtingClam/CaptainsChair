---
name: fix-bug
description: Fetch a player's bug report from the live Captain's Chair server on Fly, reproduce it, fix it with a regression test, and open a pull request whose merge deploys the fix and resolves the report. Use when asked to fix a bug report, "the newest bug", a bug by id, or to list open reports.
---

# Fix a bug report

The whole loop is in `plans/bug-pipeline.md`. In short: fetch → reproduce → test → fix → pull request. Merging the
pull request deploys to Fly and marks the report resolved (`.github/workflows/deploy.yml`). Never deploy any other
way, and never ask for Fly credentials.

## 0. Check access

`scripts/bugs.py list` needs `CC_URL` and `CC_BUG_TOKEN` in the environment and the Fly host allowed by the network
policy. If it says the variables are missing, the token was refused or the host cannot be reached, stop and tell the
user what is missing (the one-time setup in `plans/bug-pipeline.md`). If they attach a downloaded report file
instead, put it in `bugs/` and carry on from step 2.

## 1. Fetch

```bash
scripts/bugs.py list               # open reports: short id, kind, date, mode, Crews, description
scripts/bugs.py get newest         # or: get <id prefix>; saves bugs/bug-<id>.json (git-ignored)
```

A report of kind `feature` is a suggestion, not a bug: summarise it for the user instead of building it unasked.

## 2. Reproduce

```bash
cd server && uv sync --quiet; cd ..
scripts/replay_bug.py bugs/bug-<id>.json             # where it stands: last log lines, the pending decision
scripts/replay_bug.py bugs/bug-<id>.json --back 3    # step back until just before it went wrong
scripts/replay_bug.py bugs/bug-<id>.json --state /tmp/s.json   # the whole engine state, to inspect
```

Read the player's description, the log and the decision. Find the card, rule or client code involved, and the
requirement (`requirements/`) or card spec (`resources/scans/<set>/cards/*.md`) that governs it. Requirements are
the source of truth: if the player, the spec and the requirements disagree, or the bug cannot be reproduced from the
bundle, stop and ask the user rather than guess. A client-only bug (display, layout) still starts from the
report's `view`, which is what the player saw.

## 3. Write the failing test

```bash
scripts/bugs.py fixture <id>       # server/tests/bugs/<8-char prefix>.json, trimmed: no names, views or log
```

Add a test to `server/tests/test_bug_reports.py`, named `test_<prefix>`, with the player's description as its
docstring. Use `replay_fixture("<prefix>")` (or `back=`/`moves=`) from `tests/bug_replay.py` and assert the behaviour
that was wrong, not only that it replays. Run it and see it fail. If the bug is better caught by a card test
(`given(...)` in `tests/scenario.py`), add that too.

## 4. Fix

Follow CLAUDE.md: spec first, then code; `scripts/build_content.py` after editing a spec; card logic stays in its
card module; state changes only through actions. If the fix makes an old move no longer apply, the fixture test
fails with `StaleMove`: cut the fixture's commands back to the last one that still applies.

## 5. Check

```bash
scripts/start.sh --test            # every server test
cd client && npm run build         # when the client changed
scripts/replay_bug.py bugs/bug-<id>.json   # the replay now shows the corrected outcome
```

## 6. Pull request

Commit on the session's branch with the full report id in a trailer line of the message:

```
Fix <what went wrong>

<cause and fix in a sentence or two>

Fixes-Bug: <full report id>
```

Push, open a pull request (what the player saw, the cause, the fix, the test), and tell the user it is ready.
Merging it to `main` deploys and resolves the report; do not mark it resolved yourself before then.
