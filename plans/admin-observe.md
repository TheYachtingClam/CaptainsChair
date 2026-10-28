# Plan: the admin observes a game

The admin opens any game from the Admin page and watches it without taking a seat. A slider and buttons step through the game one move at a time, jump to the start of any turn, or follow the game live. Watching never changes the game: no command is stored, no seat is taken, and the players do not see the admin in their presence list. Each step ends with something you can test.

## How it works today

- A game is its setup, its seed and its list of commands (REQ-SRV-14). `play.build(game)` replays every live command (not undone, not dropped, not a note, not a tutorial move) to rebuild the `GameState`. It caches only the latest state.
- Each stored command has the seat, the option id, `irreversible`, the weekday and `turn`: `state.turn` (0-based) *before* the command was applied. The table shows `turn + 1`.
- A Bot's turn is not a command. It runs inside the human command that ends the human's turn, so in solo games one command can move `state.turn` on by 2. The view's `bot_turn` already gives that Bot turn as steps for `BotPlayback.tsx`.
- `game_view(state, viewer)` hides what `viewer` may not see. `viewer=None` is a watcher: no hands, no options, no private log lines. `GET /api/games/{id}/state` already serves this to an account without a seat (REQ-ADMIN-06's "they can still watch").
- The WebSocket refuses an account without a seat. So a watcher gets no `state_changed` pushes, and `hub.connected_seats` decides presence and the waiting emails (REQ-USER-25).
- The admin can already look at an earlier moment, but only through a bug report: Recreate copies the game from N moves earlier (REQ-BUG-07). There is no way to look at a game that nobody reported, and no way to step through one.
- Replay cost, measured on a random 418-move, 25-turn two-player game: about 0.4 s for a full replay and about 6 ms for one `deepcopy` of the state.

## Decisions

These are proposed defaults for you to confirm or change.

1. **The admin sees everything by default.** All hands, Draw deck order, facedown Bot cards, every private log line, and the options of the pending decision, shown but not clickable. A **View as** switch shows the game as either seat (or as a watcher) sees it, to check what a player could see. This is in line with REQ-BUG-05: the admin already reads bundles that hold every hidden card.
2. **One step is one stored move.** A move is a player's answer to one decision, or a developer command. Undone and dropped moves are skipped, as in replay. Tutorial coaching moves and notes are skipped too, because they do not change the table. A Bot turn is part of the move that ended the human's turn; when you stand on that move, the existing Bot playback panel plays the Bot's turn back step by step.
3. **Turn numbers are the table's.** "Turn 7" is the 7th turn of the game, counted as the table counts it (`state.turn + 1`), so in a two-player game turns 1, 3, 5… belong to the first player. **Go to turn N** opens the position just before the first move of turn N (its Resupply). A Bot's turn N opens the position just after the human move that started it, with its playback.
4. **Watching is read-only, and never writes.** The observer's replay must never run `play._drop_from`, which saves to the database. If the rules changed so that a move no longer applies, the timeline ends there and shows why; the game is left untouched. To play on from an earlier moment, **Copy from here** makes a playable copy, the same way Recreate does for a bug report (REQ-BUG-07).
5. **Live follow.** When the slider is at the last move, the view follows the game as it is played (pushed over the WebSocket). When the admin steps back, it stops following and shows "N moves behind; Back to live".
6. **The admin is invisible to the players.** An observer's socket is not a seat: it does not show in presence and does not stop a waiting email.

## Design

### Positions and the timeline

A **position** `p` (0 to `n`) is the state after the first `p` live moves; position 0 is the table right after setup. The timeline is one row per position:

```json
{"at": 12, "turn": 3, "active": 0, "step": "action", "seat": 0, "move": "Play Utilize", "irreversible": false,
 "dev": false, "bot_turn": null}
```

- `move` is the label of the option chosen to reach this position. It is read from the decision during replay, because commands store only the option id.
- `bot_turn` is the Bot's turn number when this move ran a Bot turn.
- The timeline also lists `turns`: for each turn, its number, its player (or the Bot) and the position it opens at.

### Where it lives

- `server/app/observe.py`: `timeline(game)` and `state_at(game, at)`. They are pure: they build from a detached copy of the commands and never touch the row or the database.
  - Replay once to build the timeline, keeping a `deepcopy` of the state at the start of each turn as a **checkpoint**. On the measured game that is 25 checkpoints, about 150 ms more than a plain replay.
  - Cache them in memory per game, keyed like `play.build`'s cache (commands count and live count), and keep only the last few games watched. A new move extends the timeline from the latest state without replaying it all again.
  - `state_at(at)` takes the nearest checkpoint at or before `at` and replays the moves after it: at most one turn's moves, a few tens of milliseconds.
  - `play.build` and `observe` share one replay loop (`play.replay(game, upto=None, on_move=None)`), so the two can never disagree. Only `build` acts on a move that no longer applies (it drops it and saves); `observe` stops and reports it.
- `engine/views.py`: `game_view(state, viewer, *, omniscient=False)`. With `omniscient`, every player is drawn as `mine` (hands, deck order, facedown cards), every log line is included, and the decision carries its options with `"observe": true` so the client shows them without letting anyone pick one. No other change to the ordinary views.
- `server/app/routes/admin.py`:
  - `GET /api/admin/games/{id}/timeline`: the positions and turns above, plus `live` (the last position) and `stopped` (why the timeline ended early, if it did).
  - `GET /api/admin/games/{id}/observe?at=p&as=all|0|1|watcher`: the view at position `p` (the last position when left out), with `observe: {at, live, turn}`. `can_undo` and `dev_tools` are false, and the tutorial block is left out.
  - `POST /api/admin/games/{id}/copy {"moves": p}`: a playable copy from position `p`, every seat the admin's. It reuses `bugs.as_game` with a bundle built from the live game (`bugs.bundle` without the reporter's part). The copy never counts for a campaign.
- `server/app/routes/ws.py` and `hub.py`: an admin without a seat may open the socket as an **observer**. Observers are kept in their own set per game. They receive every broadcast, but `connected_seats` and the presence message leave them out.
- Client:
  - `/admin/games/:gameId/observe?at=p&as=all` is a new page, `pages/Observe.tsx`. The URL holds the position, so a reload or a shared link (to another admin) opens the same moment.
  - The Admin page's games table gets a **Watch** button per started game.
  - The page draws the ordinary `Board` with the observed view in read-only mode: no answer buttons, End Turn, Undo, Report a bug or Dev panel. `Board` gets a `readOnly` prop; the options of the pending decision are shown greyed with "(<player> is deciding)".
  - Above the board, an **observer bar**: |◀ (start), ◀◀ (previous turn), ◀ (previous move), ▶ (next move), ▶▶ (next turn), ▶| (live), a slider over all positions, a **Turn** box with Go, the move list (the timeline's labels grouped by turn, click to jump), **View as**, and **Copy from here**. Keyboard: ← and → step a move, Page Up and Page Down step a turn, End goes live.
  - On a phone the bar is a compact row (◀ ▶, turn box, a ⋯ menu for the rest) above the bottom sheet.
  - Prefetch the next and previous positions so stepping feels instant.

## Steps

### Step 1: Requirements (done, awaiting your review)

- `requirements/19-technical-architecture.md` §5.6: new REQ-ADMIN-07 to -12 for watching (open any game, the view and what it hides, positions and stepping, going to a turn, live follow and invisibility, Copy from here, read-only). Add the three endpoints to the endpoint table and the Observe page to the screens table.
**You test:** read REQ-ADMIN-07 to -12 and correct anything that is not what you want.

What was done: `requirements/19-technical-architecture.md` §5.6 has a new part, "Watching a game", with REQ-ADMIN-07 (the Watch button and the read-only Observe page), -08 (everything shown, View as), -09 (positions, moves, stepping, the move list, keys, the address), -10 (Go to turn and Bot turns), -11 (live follow, unseen) and -12 (Copy from here). Also updated: the three endpoints (§3.5), REQ-SRV-40 (the admin may open the socket without a seat) and -44 (a watching admin is never counted as connected), the Observe page in the screens table (§4.2), and the README's note that spectators are out of scope (only the admin can watch).

### Step 2: Replay one move at a time on the server (done)

- `play.replay(...)` shared by `build` and `observe`; `observe.timeline` and `observe.state_at` with checkpoints and the cache.
- A line in `CLAUDE.md` under the engine's server bullets pointing at `app/observe.py`.
- Tests (`tests/test_observe.py`):
  - position 0 is the setup;
  - the last position equals `play.build`;
  - every position equals a plain replay of that many moves, on a random two-player, solo and Cadet game;
  - undone, dropped, tutorial and note entries are skipped;
  - a turn opens where its first move starts;
  - a solo Bot turn is found on the human's move and its `bot_turn` is in the view;
  - a move that no longer applies ends the timeline, and the stored commands are unchanged;
  - extending the timeline after a new move gives the same result as building it fresh.

**You test:** nothing to click yet; the tests and a timing print for a long game.

What was done:
- `play.replay(commands, state, start)` is the one replay loop. It yields each move's index just before applying it, so a caller stops at any position by stopping the loop, and raises `StaleMove` for a move that no longer applies. `play.build` uses it and still drops such moves; `play.initial` is the state just after setup; `play.is_move` says which stored commands are moves.
- `app/observe.py`: `timeline(game)` gives `last` (the last position), `moves` (per move: the position it reaches, its command index, turn, seat, the question and the label of the answer, irreversible, developer), `turns` (per turn: number, seat, name, whether it is the Bot's, and the position it opens at) and `stopped`. `state_at(game, at)` gives a copy of the state at a position. Checkpoints are kept at the start of each turn and every 40 moves within a long turn; the last 4 games are cached, and a game that has only gained moves is extended rather than replayed. `play.forget` forgets the timeline too.
- The design's `bot_turn` per move became `bot` on each turn in `turns`: a Bot's turn opens at the position after the human move that ran it.
- Tests (`tests/test_observe.py`, 12): every 5th position of random two-player, solo and Cadet games equals a plain replay, and the last equals `play.build`; labels; turns open before their first move and alternate; a solo Bot turn opens after the move that ran it, with its playback in the view; undone, dropped, tutorial and note entries are not moves; a move that no longer applies ends the timeline and leaves the commands untouched; extending equals a fresh build; an undo rebuilds; checkpoint spacing; the cache keeps 4 games.
- Timing on a random 405-move, 26-turn two-player game: the timeline is built in 0.57 s (once; then cached), and the slowest of 40 random positions took 0.06 s.

### Step 3: The view and the endpoints (done)

- `game_view(..., omniscient=True)` and the three admin endpoints.
- Tests:
  - an account that is not admin gets 403 on all three;
  - `as=0` hides seat 1's hand, and `as=all` shows both hands with the pending options marked `observe`;
  - `as=watcher` matches what an unseated account gets from `/state`;
  - watching stores nothing (the commands list and status are unchanged);
  - Copy from here makes an active game with `p` moves and the admin in every seat, and a campaign copy carries no campaign id.

**You test:** call the endpoints from the browser's address bar while signed in as admin.

What was done:
- `game_view(state, viewer, omniscient=True)`: every hand, every Draw deck and Reserve deck (and the Bot's Supplement deck) in order, the Bot's facedown cards with their faces and `"facedown": true`, every log line and Bot playback step, and the pending decision's options and cards with `"observe": true`. The ordinary views are unchanged.
- `GET /api/admin/games/{id}/timeline` (the Step 2 timeline), `GET /api/admin/games/{id}/observe?at=&as=` (`as` is `all`, `watcher` or a seat number; the view adds `observe: {at, last, live, as}`, with `can_undo` and `dev_tools` false) and `POST /api/admin/games/{id}/copy {"moves": p}`. A game that has not started gives 409, a position outside the timeline or an unknown `as` 422.
- `observe.cut(game, at)` gives how many stored commands make up position `at`; the copy keeps exactly those. Recreate and Copy from here share one helper (`_copy` in `routes/admin.py`).
- `bugs.setup(game)` is the setup part of a bundle, shared by bug reports and copies. It now includes a tutorial's setup (script, seed, stacked decks), which `bugs.as_game` restores. Before, a bug report from a tutorial game was rebuilt without its stacked decks and dealt different cards; REQ-BUG-03 now says so.
- Tests (`tests/test_observe.py`, 7 more): the three endpoints need the admin; everything is shown with `as=all`; `as=0` matches exactly what that player gets and hides the other hand; `as=watcher` matches a seatless account's view; positions, `live` and out-of-range errors; watching leaves the commands, status and seats untouched; Copy from here gives the game at that position with every seat the admin's, playable at once; a campaign game's copy has no campaign id; a tutorial's copy deals the same cards (checked to fail without the fix).

### Step 4: Live follow without being seen

- The observer socket in `ws.py` and `hub.py`.
- Tests:
  - an admin without a seat connects as an observer and gets `state_changed` after a player's move;
  - presence does not list the observer;
  - a waiting email is still sent while only the admin has the game open;
  - an account that is neither seated nor admin is still refused.

**You test:** watch a game from the Admin page in one browser and play it in another.

### Step 5: The Observe page

- `pages/Observe.tsx`, the observer bar, `Board`'s `readOnly`, the Watch button, keyboard keys and the phone layout.
- `cd client && npm run build` must pass. Check with Playwright on a laptop and a phone width: step through a whole solo game, go to a turn, play a Bot turn back, switch View as, follow live, and make a copy.

**You test:** watch one of your own finished games from turn 1 to the end, and jump to a turn you remember.

### Step 6: Test pass and deploy

- `scripts/start.sh --test`, the client build, and a final look at the Admin page.

**You test:** use it on the real server.

## Risks and notes

- **Rules changes.** A game played under older rules may stop replaying part-way. The observer shows the timeline up to there and says why; the game is only repaired (moves dropped) when a player next opens it, as today.
- **Memory.** Checkpoints are full states. Keeping a handful of games and one checkpoint per turn is a few MB; the cache drops the oldest game first.
- **Hidden information.** The omniscient view exists only behind `require_admin`, and the ordinary views do not change. A test checks that `/state` for a player never contains the other hand.
- **The weekday.** Each move replays with its stored weekday (REQ-SRV-52), so U.S.S. Enterprise-B looks the same when watched as it did when played.
- **Not in this plan.** Watching for players (a public spectator mode); stepping inside a single operation's questions (they are separate moves already); showing undone moves on the timeline; editing a game's history.
