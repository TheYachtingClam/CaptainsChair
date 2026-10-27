# Plan: playing on a phone

The game table was built for a laptop. This plan makes a game playable on a phone held upright, from 375 pixels wide, without changing the laptop layout. The requirements are REQ-CLI-18 and §4.4 of [19-technical-architecture.md](../requirements/19-technical-architecture.md) (REQ-CLI-30 to -36). Each step ends with something you can test.

## How it works on a phone today

| Piece | Now | Problem |
|---|---|---|
| Reading a card | The enlarged card and its beamed cards appear on hover; on a touch screen that preview is switched off (`@media (hover: none)` in `styles.css`) | A tap opens the action panel, which shows only your own cards. An opponent's card, a Market card or a Location cannot be read at all |
| The table | Opponent's mat, centre and your mat in one long column; at under 480 pixels cards shrink to 64 pixels | Following a turn means scrolling up and down all the time |
| Floating panels | The question box (bottom), the card panel and the Bot or opponent turn panel (top right) are all fixed on the screen | On a small screen they cover most of the table and each other |
| Hover-only details | Hand cards lift on hover; Ship and Away Team tokens name themselves on hover | Never happens on a phone |
| Tap targets | Cards at 64 pixels, some small buttons and badges | Hard to hit with a finger |

## Decisions

Taken as the defaults on 2026-10-27; say if you want any of them changed.

1. **Portrait.** The phone layout is for a phone held upright. Sideways must not break, but gets no layout of its own.
2. **One area at a time, with tabs** (You, Centre, Opponent, Log) rather than one long page with jump buttons. More work, much easier to follow a turn.
3. **Press and hold to inspect a card**, with a one-time hint, rather than a magnify icon on every card. A short tap keeps its meaning (select, or answer).
4. **When it counts as a phone:** narrower than 700 pixels. The no-hover rule (REQ-CLI-30) applies to every touch screen, tablets included.

## Steps

### Step 1: Requirements and a way to test (done)

- REQ-CLI-18 now asks for phones; the new §4.4 "Phones" has REQ-CLI-30 to -36.
- `scripts/start.sh --dev --host` runs the dev servers so a phone on the same Wi-Fi can open the client: Vite prints a "Network" address such as `http://192.168.1.20:5173`; open it on the phone. Sign-in works over plain HTTP locally because the local `.env` has `SECURE_COOKIES=false`.
- The local Docker server also listens on the network, at `http://<this computer's address>:8000`, which is enough for looking at a deployed build. Stop it (`docker compose stop`) before `--dev`, which needs port 8000.
- For layout, Chrome's device toolbar (an iPhone SE is 375 pixels wide) is quicker; touch needs a real phone, or the Fly site once a step is deployed.

**You test:** open the lobby on your phone through the network address, sign in, and look at a game as it is today.

Done ahead of Step 2, because it was the most distracting thing on a phone: under 900 pixels the Crew board was drawn the full width of the mat. It is now at most 240 pixels wide (46% of the mat), beside the tokens, and a tap shows it full size (`CrewBoard` in `PlayerMat.tsx`).

### Step 2: Inspect any card by touch (REQ-CLI-30, -31) (done)

- A shared `useLongPress` hook: about 450 milliseconds of holding without moving opens the viewer, and the tap that follows the release is swallowed so it does not also select the card.
- A full-screen card viewer: the card as large as fits, the cards beamed to it, and its tokens. Reuses what the hover preview shows (`Cards.tsx`). Tap anywhere to close.
- Wired to every card on the table and in pile viewers, and to Ship and Away Team tokens.
- The one-time hint, remembered in the browser.
- Hand cards stop lifting on hover where there is no hover.

**You test:** in a game on the phone, read an opponent's card, a Market card and a Location, and see the cards beamed to a Ship. A tap on your own card still opens its actions.

What was done: `useLongPress` and `CardViewer` in `Cards.tsx`, opened through `InspectContext` (provided by `Board.tsx`). Every `Card` (including beamed ones), Ship tokens at Locations, Crew boards and the Bot's command cards open the viewer on a 450 ms press; a mouse is ignored, since it has hover. The viewer shows the card, its resources and Ship token, and the cards beamed to it, each of which opens in turn. The press's own click is swallowed, and the viewer ignores taps in its first 400 ms, so the finger lifting does not close it. A tap on a Crew board opens it too. The phone's own long-press menu is turned off on cards (`-webkit-touch-callout: none`). The hint is shown once (`cc.hint.hold` in local storage). Hand cards lift on hover only where there is hover.

Found on the way: on every narrow screen the table was wider than the window, because a later `.mat-grid` rule overrode the narrow layout, so on a phone everything was cut off on the right and the boards looked huge. Fixed; the page now fits a 390-pixel screen exactly.

Checked with Playwright on an emulated iPhone 13: holding a Market card opens the viewer and does not select it; a tap closes it; a short tap on a hand card still opens its actions; holding a Crew board opens it wide; no element is wider than the screen.

### Step 3: Questions and panels as one bottom sheet (REQ-CLI-34) (done)

- Under 700 pixels, the question box, the card action panel and the turn playback panel open as a sheet from the bottom instead of floating.
- The sheet collapses to one line that still says what is asked ("Choose a Ship to warp") and opens again with a tap.
- Only one sheet at a time; the playback panel waits behind a pending question as it does today.

**You test:** play a solo game: answer questions, use a card's actions, step through the Bot's turn, all without anything covering the cards you need.

What was done: `components/Sheet.tsx` has `usePhone()` (under 700 pixels) and `Sheet`, which on a laptop is the panel's own floating box and on a phone a block with a 44-pixel handle: the summary (the question, the card's name, or "Soval Bot's turn · step 3 of 20") and Hide or Show. A collapsed block opens again on a new question, a new card or a new turn (`openOn`), not on every step. `Board.tsx` puts the turn playback, the question box, the waiting notes and the card panel in one `.sheet-stack`, which on a phone is fixed to the bottom (at most 70% of the screen, each block scrolling inside) and on a laptop is `display: contents`, so nothing moves there. The table gets bottom padding equal to the sheet's height (a `ResizeObserver`), so the hand can always be scrolled into view above it. Inside the sheet: the question is not repeated under the handle, dock cards and the card image are 84 pixels, the card panel keeps its ✕, and the playback buttons are 44 pixels high.

Checked with Playwright on an emulated iPhone 13: a hand card's panel opens at the bottom, collapses to 46 pixels and closes with ✕; a question and the Bot's turn sit at the bottom with the "press Done" note under them; nothing is wider than the screen. At 1280 pixels the panels float as before and no handles appear.

### Step 4: One area at a time (REQ-CLI-32, -33)

- Under 700 pixels, `Board.tsx` shows one of You, Centre, Opponent and Log, chosen from a bar at the bottom (above the collapsed sheet).
- A tab gets a mark when something there changed since it was last shown.
- When a question asks for cards, the area holding them is shown: the Market for a gain, the Neutral Zone for a warp, your hand for a discard.
- Your hand becomes one row that scrolls sideways.
- The laptop layout is untouched.

**You test:** a two-player game against yourself in two browsers, one of them the phone: follow the opponent's turn from the tabs, then play yours.

### Step 5: Touch polish (REQ-CLI-35, -36)

- Tap targets of at least 44 pixels on a phone; no sideways page scroll.
- The top bar, lobby, new game, campaign, account, sign-in and Admin pages checked at 375 pixels and fixed where needed.
- Double-tap zoom off on the table, so fast taps are not taken as zoom.

**You test:** walk through every page on the phone.

### Step 6: A full test pass

- A whole solo game, a whole two-player game and a campaign assignment on a real phone; fix what turns up.
- Deploy to Fly.

**You test:** play on the phone for real.

## Risks and notes

- **Two layouts to keep working.** Every later change to the table needs a look at both. Keeping the phone layout in CSS and a few `usePhone()` checks in `Board.tsx`, not a second table, keeps that small.
- **Long press and the browser.** Phones open their own menu (save image, share) on a long press on an image. The card images need `-webkit-touch-callout: none` and no text selection, or the viewer and the menu both appear.
- **Screen space for the Bot's command card.** The playback highlights a row on the Bot's command card; on a phone that card needs the sheet's full width to be readable. Checked in Step 3.
