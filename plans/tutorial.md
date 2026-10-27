# Plan: the first tutorial, "Learn to play with Picard"

A new player opens the tutorial from the lobby and plays a real game of *Captain's Chair* with Jean-Luc Picard's Core Box deck while a coach explains each part as it comes up. It is the first of several tutorials (later ones teach a specific Captain or a new feature), so this plan also builds the tutorial framework they will reuse. Each step ends with something you can test.

## What the player should know at the end

Taken from the rules, in the order they come up in play:

| # | Lesson | Rules |
|---|---|---|
| 1 | How to win: VP, Glory, and how the game ends (Stardates, the Burn) | 01, 07, 13 |
| 2 | Your table: Captain, Crew board and its tracks, hand, Draw deck, Discard pile, Reserve, Development pile, Staging Area, Fleet, Locations, Duty Officers, the Captain's Log | 04, 12 |
| 3 | A turn: Resupply, Control, Action Step (3 actions), Clean-up | 05, 06, 07 |
| 4 | Playing cards: action cost, free effects, resources (Dilithium, Latinum, Glory) | 06, 08 |
| 5 | The Market: gaining, scanning, the Junk | 08, 14 |
| 6 | Ships: deploying, warping, beaming cards to a Ship | 09 |
| 7 | The Neutral Zone: sending Away Teams, securing a Location, taking control of it | 05, 09 |
| 8 | Duty Officers and Specialty tracks | 06, 10 |
| 9 | Reactions (Picard: after gaining an Ally, beam it to a Ship for Glory) | 06, 14 |
| 10 | Incidents and returning them | 08, 14 |
| 11 | Clean-up: discard, draw up, deck cycling, enlisting a Reserve card; Developments | 07, 08 |
| 12 | Logging cards | 11 |
| 13 | Missions (Peace Negotiations: 3 Allies on one Ship and two tracks at 4) | 10 |
| 14 | Final scoring | 13 |

Interaction with an opponent (attacks, contested Locations) is left to a later tutorial; this one ends by pointing at solo play against a Bot.

## Decisions

Decisions 1 and 2 confirmed on 2026-10-27; 3 to 5 are proposed defaults.

1. **Game mode: Cadet Training.** One player, no opponent's turns to wait through, a fixed 11-turn length and a VP rating at the end (REQ-CTM-01 to -23). The coach explains the virtual opponent where it matters ("one of everything"). The alternative, a game against a Bot, teaches more but doubles what the player has to follow.
2. **On rails at first, then free.** Turns 1 to 3 are scripted: the coach says what to do and only that move is allowed, so every lesson happens on cue. From turn 4 the player plays freely; the coach adds a tip the first time something new happens (first Incident, first deck cycle, first mission ready, the Stardate emptying). The player can leave the rails early with "Let me play".
3. **A stacked deck.** The tutorial fixes the order of the player's Draw deck, the Market decks, the Location deck and the Incident deck, so the scripted turns always have the right cards. After the scripted turns the order is random as usual (from the tutorial's seed).
4. **The tutorial's text is written for you to review before it is built.** It is the largest part of the work, and it has to be right about the rules.
5. **Tutorials are data.** Each one is a YAML file of steps (`server/content/tutorials/<id>.yaml`) with its setup; the framework does not know about Picard, so later tutorials are new files, not new code.

## Design

### A step

```yaml
- id: play-utilize
  say: |
    **Utilize** gives Dilithium, the resource most cards spend. Playing it costs one of your three actions.
    Tap Utilize in your hand and choose its first effect.
  show: card:1PIC19          # what to highlight: a card, a zone, a button or a tab
  expect: play:1PIC19:0      # the move this step waits for; other moves are greyed out
- id: dilithium
  say: You now have 1 Dilithium; it is shown with your resources.
  show: zone:resources
  next: button               # an explanation only: the player taps Next
```

- `show`: a card (by card id, so the script needs no uids), a zone (`hand`, `market:Ship`, `neutral-zone`, `resources`, `tracks`, …), a button (`end-turn`, `undo`) or a tab on a phone.
- `expect`: one or more moves, written with card ids instead of uids; the server translates them for the current game.
- `next: button` for explanations; `when:` for a tip that waits for something to happen (`event: take_incident`, `decision: mission`, …).

### Where it lives

- **Engine:** no tutorial logic. It gains only a way to stack decks at setup (a `stack` option to `new_game`), stored with the game like the seed so replays and undo still match.
- **Server (`app/tutorial.py`):** loads the scripts, works out the current step from the game's moves (so undo steps back too), removes the moves a step does not allow from the decision it sends, and adds a `tutorial` block to the view: the step's text, what to show, progress (step 7 of 52), and whether Next is needed. A game has a `tutorial` column with the script's id.
- **Client:** a coach panel and a spotlight. On a laptop the coach floats beside what it points at; on a phone it is a block in the bottom sheet and switches to the tab that holds the target. Highlights use `data-tutorial` attributes on the table's elements. Buttons: Next, Back (for explanations), "Let me play", Leave tutorial.
- **Lobby:** a "Learn to play" card for players who have not finished it, and a Tutorials list (one entry for now). The account remembers finished tutorials.

## Steps

### Step 1: Requirements and the script (for your review) (done, awaiting your review)

- `requirements/24-tutorials.md`: REQ-TUT rules for the framework (step kinds, rails, tips, progress, undo, phone and laptop) and for this tutorial.
- `server/content/tutorials/picard-basics.yaml`: every step's text, the stacked decks and the scripted moves for turns 1 to 3, and the tips for free play. Written against the card specs, with the rule each lesson comes from.
- A short summary of the scripted turns for you to read first:
  - **Turn 1:** the goal of the game, resources, Picard, the Crew board, the Ship, the hand and the turn. Utilize (an action). Set a Course's free PLAY: draw, discard Analyze, warp the Enterprise-D to Indri VIII. The Market. Recruit: take an Incident to gain Tholians; Picard's Reaction discards the Incident for 1 Glory and beams Tholians to the Enterprise-D. Diplomacy: gain Bolians on top of the deck and log Diplomacy (the Captain's Log). Clean-up: wipe Arin'sen, 1 Glory on Halkan Council, draw up.
  - **Turn 2:** Worf sends 2 Away Teams to Verex III. Will Riker takes Utilize and Recruit back from the Discard pile and sends a third Away Team: Verex III is secured. Red Alert returns itself (Bolians goes on top of the deck) and promotes Will Riker from the Staging Area to Duty Officer. Clean-up again.
  - **Turn 3:** the deck ran out (shuffling and enlisting a Reserve card). Resupply: Riker gains 1 Latinum. Control: take Verex III (and why the Ship stayed away). Farpoint Station, a Crew Location (1 Research). Utilize for 5 Dilithium. Recruit Halkan Council and its 2 Glory; Picard beams it aboard. Type 7 Shuttlecraft beams Bolians aboard: three Allies on one Ship. The mission's other half (two tracks at 4).
  - **Turns 4 to 11:** free play with tips; Peace Negotiations when it comes within reach; the first Stardate emptying; final scoring and the rating.

**You test:** read the script and correct anything that is unclear or wrong.

What was done: `requirements/24-tutorials.md` (REQ-TUT-01 to -63) and `server/content/tutorials/picard-basics.yaml`: 63 steps (47 of them moves, the rest explanations with Next) and 10 tips. The script was drafted by playing the stacked game in the engine move by move, and the whole file was replayed from the YAML, translating each `expect` the way the server will: every move exists, in order, ending at turn 4 with Verex III and Farpoint Station controlled, Will Riker as Duty Officer, Tholians, Halkan Council and Bolians on the Enterprise-D, and Diplomacy in the Log.

Changed from the first outline while drafting:
- Taking control of a Location dismisses every Ship there (REQ-CON, rules 05). The first draft had the Enterprise-D help secure Verex III and lose itself and Tholians when Verex III was taken. Now the Enterprise-D warps to Indri VIII, Verex III is secured with 3 Away Teams (Worf's 2 and Will Riker's 1), and the coach explains why the Ship stayed away.
- Promoting a Duty Officer comes from **Red Alert** (from the Staging Area), which also teaches the Staging Area and returning an Incident; only one Duty Officer at a time.
- Strange New Worlds would log Verex III just after it is taken, which confuses at this point, so it became a free-play tip. Developments too: they are only offered once the Reserve deck is empty (REQ-DK-10), which happens in free play.
- The deck runs out during turn 2's Clean-up, so deck cycling and the Reserve are explained at the start of turn 3; Type 7 Shuttlecraft, the enlisted Reserve card, is then drawn and played.

### Step 2: Stacked setup and the tutorial on the server (done)

- `new_game(..., stack=…)`; the tutorial's setup stored with the game.
- `app/tutorial.py`, the `tutorial` view block, move filtering, and an endpoint to start a tutorial game.
- Tests: the scripted moves replay to the end of turn 3 with the stacked decks; a move the step does not allow is refused; undo goes back a step; the stacking does not change ordinary games.

**You test:** start the tutorial through the API and step through it with the existing table (no coach yet).

What was done:
- Engine: `new_game(..., stack=…)` (`setup._apply_stack`) orders the first player's hand and Draw deck, Reserve deck, face-up Market cards, the top of Market decks, the Neutral Zone (swapping a Location already in another slot) and the top of the Incident deck. It uses no randomness, so later shuffles follow the seed (a test checks the RNG count is unchanged).
- Server: `Game.tutorial` holds the script's id, seed and stack, so a tutorial starts with the script's seed and replays with the stack it began with. `app/tutorial.py` loads the scripts, works out the step from the moves (`progress`), translates `expect` into the real answer (`resolve`), and gives the allowed answers (`allowed`) and the coach's block for the view (`block`). Next and Let me play are stored as moves (`tutorial:next`, `tutorial:free`) that the engine never sees (`play.coaching`), so undo steps the coach back.
- API: `GET /api/tutorials`, `POST /api/tutorials/{id}` (starts a game), `POST /api/games/{id}/tutorial/next|free`. A move the coach is not waiting for is refused with 409; the view marks such answers `disabled` and adds `tutorial`: title, step index and total, the step's text, what to show, whether it needs Next, and whether the rails have ended. Game summaries carry `tutorial` (the script id).
- Tests (`tests/test_tutorial.py`): the Picard script played through the API exactly as a client would, all 63 steps, ending in free play on turn 4 with the expected table; other moves refused and Next refused on a move step; undo steps back; Let me play; ordinary games have no coach; stacking.

The existing table cannot show the coach yet (it has no Next button), so the tutorial is only playable through the API until Step 3.

### Step 3: The coach on the table (done)

- The coach panel and spotlight, on a laptop and on a phone (a block in the bottom sheet; switches tabs).
- `data-tutorial` targets on the table's cards, zones and buttons; moves the step does not allow are greyed out.
- Next, Back, "Let me play", Leave tutorial.

**You test:** play the scripted turns on your phone and laptop.

What was done: `components/Coach.tsx`, the coach: the tutorial's title, "Step n of 63", a progress bar, the step's text (with **bold**), Back (an ordinary undo, shown when there is something to undo), Next (on explanations), Let me play and Leave tutorial. On a laptop it floats in the top-right corner; on a phone it is the first block of the bottom sheet, collapsible like the others. `coachTarget` finds what a step points at from `data-tutorial` names on the table (resources, tracks, captain, hand, fleet, locations, duty, staging, deck, discard, reserve, development, end-turn, market, market:<suit>, neutral, stardate, incident) and `data-card-id` on cards, looking in your own mat first. The board highlights it (a pulsing yellow outline, nothing blocked), and also the matching answer button when the card is an answer in the question box; once per step it scrolls the target into the middle of the space the bottom sheet leaves free. On a phone it first switches to the tab that holds the target (Market, Stardate and Incident on Centre; the Neutral Zone and everything of yours on You). Disabled answers (REQ-TUT-23) are greyed out in the question box and left out of playable cards, card panels, clickable targets, End Turn and missions. The lobby has a simple Learn to play card that starts the tutorial (polished in Step 4).

Checked with Playwright on a 1280-pixel laptop and an emulated iPhone SE: all 63 steps, Next taps through the coach's own button, and at every step the coach shows the step's text and what it points at is on screen and not covered (by the sheet, the coach or anything else). Two fixes came from it: the coach's scroll now runs just after the question's own scroll to its cards, and it centres in the space above the bottom sheet rather than the whole screen.

### Step 4: Free play, tips and the end (done)

- Tips that wait for an event or a kind of decision, each shown once.
- The end: final scoring explained line by line, the Cadet rating, and "Play against a Bot next".
- The lobby's "Learn to play" card and Tutorials list; the account remembers a finished tutorial.

**You test:** play the whole tutorial to the end.

What was done: tips (`tutorial.tip`, REQ-TUT-31, -32): after the guided part, the first tip in the script's order whose trigger holds and that has not been closed shows in the coach with **Got it** (stored as a `tutorial:tip:<id>` move, so undo brings it back) and, for the last one, a **Play against a Bot** link. Triggers read the game as it is: a question (a claimable mission, or an Encounter or Development question by its words), a playable card, a track value, an Incident in hand, or a moment (the first Stardate used up, the last turn, the game's end). The game's end shows the final-scoring tip over the score breakdown and Cadet rating, then the closing tip. The lobby's Learn to play card is highlighted until the first tutorial is finished, offers **Continue** and **Start again** for a tutorial in progress, and marks finished ones (`GET /api/tutorials` reports `finished` and `game_id` per account); tutorial games are labelled "Tutorial" in Your games.

### Step 5: Test pass and deploy (the emulated pass done; your play-through and the deploy to come)

- A Playwright run through the whole tutorial on an emulated phone and a laptop (the player from the phone plan's Step 6, following the coach).
- Fixes from your play-through; deploy.

Done so far: a Playwright player started the tutorial from the lobby's Learn to play card on an emulated iPhone SE and on a 1280-pixel touch laptop, followed the coach through all 63 steps, then played freely to the end of turn 11, reading and closing each tip: Strange New Worlds, Incident in hand, the first Stardate, enlisting a Development, the last turn, final scoring and the closing tip with its Play against a Bot link. Afterwards the lobby showed the tutorial as Finished. No page errors and no taps blocked. (The Encounter, track and mission tips did not come up in that random game.)

## Later tutorials

A new tutorial is a new YAML file: its setup (Captain, box, stacked decks, mode) and its steps. The framework's step kinds, tips and coach serve all of them. A tutorial that needs an opponent (attacks, contested Locations) uses solo mode against a Bot instead of Cadet Training; the script then also covers the Bot's turns.

## Risks and notes

- **The script must match the cards.** If a card's code or the rules change, a scripted move may no longer exist. The replay test in Step 2 fails when that happens, so it is caught before players see it.
- **Text length on a phone.** Each step's text is kept to two or three short sentences; longer explanations are split.
- **Rails that are too tight feel like a slideshow.** Only turns 1 to 3 are on rails, and "Let me play" is always there.

## Revision 1: your first play-through (2026-10-27)

Your notes, each with what to change. Where I think a note would overload a new player or is not quite the rule, it says so (**push back**). Step numbers are the script's order (step 4 is `captain`, 43 `draw-up-2`, and so on).

### Two new tools, to add depth without a wall of text

The notes ask for a lot more explanation. A first game already has 63 steps; adding everything as plain text would double the reading and lose people. So:

1. **"More" on a step** (`more:` in the script): the step's text stays two or three sentences, and a **More** link opens the extra detail for players who want it. The why-it-matters and strategy notes go there.
2. **A "How cards work" sheet**, opened from a **?** in the coach at any time: where each kind of ability works (below), the icons, and the words used (gain, discard, dismiss, log, beam, secure, enlist). The coach links to it at the first Reaction and the first Activation instead of explaining everything at step 8.

Where each kind of ability works (rules 06 §6, 05, 07; to be confirmed against the engine while writing the sheet):

| Where the card is | What works |
|---|---|
| Hand | PLAY (playing it), and SUPPORT in expansions |
| Staging Area (played this turn) | Only CLEAN-UP, at the end of the turn |
| Table positions: Captain, Status, Fleet Area, Location Area, Duty Officer | Blue strip (ACTIVATION, PASSIVE, REACTION), RESUPPLY, CLEAN-UP; ENDGAME at the end |
| Beamed onto a Ship or Location | Nothing (it travels with its host; it still scores) |
| Captain's Log | Nothing (it still scores) |

3. **Icons in the coach's text and card panels.** There are no icon images yet: cards show "[Action]" as text. Crop the Action, Dilithium, Latinum, Glory, Research, Influence, Military and Away Team icons from the rulebook's reference pages (`scripts/process_scans.py`) and draw them in place of `[Action]`, `[Dilithium]`, … in the coach and in card panels.

### Your notes

| # | Note | Decision | Change |
|---|---|---|---|
| Start | Glory can be spent as Latinum or Dilithium | Agree, with the exact rate | Step 3: "When you pay, 1 Glory can stand in for 1 Latinum or 2 Dilithium (no change given), but each Glory spent is a VP lost." (KW-SPEND-02) |
| Start | 11 turns here; normally the Stardates | Agree | Step 2: "This practice game lasts 11 turns. In a real game it ends when the Stardate cards run out of Glory." |
| — | The Burn is scary at the end | Agree | Step 2's More: the other ending, the Burn (Incident deck empty: the game ends at once; in practice you lose). The Incident tip later just reminds. |
| 4 | "Reaction" comes out of nowhere; blue abilities only from deployed cards | Agree; the rule is "table positions", not only deployed | Step 4: what a Reaction is ("an ability that fires by itself when something happens; you choose whether to use it"), with a link to How cards work. The blue-strip rule goes in step 9's More and in the sheet: blue abilities work only while the card is in a table position (Captain, Fleet, Locations, Duty Officer), never from your hand, the Staging Area or beamed. |
| — | A main goal is burning through your deck to reach Developments | **Push back** on "main goal": the goal is VP. Cycling your deck fast is a key strategy because each reshuffle enlists a Reserve card and, once the Reserve is empty, lets you enlist a Development | Taught at step 44 (deck cycling), with the card kinds (below), and in the discard notes (43) |
| 5 | How you move along the tracks and why | Agree | Step 5: "Cards move your markers: 'gain 1 Research' moves Research one space; Utilize moves them for the Skill icons you have in play." More: why: some cards need a track value ("Requires Military 3"), Picard's mission needs two tracks at 4, and marked spaces multiply your Focus cards' VP at the end, once you've completed a mission. |
| 8 | Which areas each kind of ability works in | **Push back** on putting it all at step 8: it is the hardest table to absorb before you've played a card | Step 8 stays about the four steps, plus one line: "What a card can do depends on where it is: see **How cards work**." The table above is the sheet. The coach points to it again at the first Reaction (18) and the first Activation. |
| 9 | Show the Action icon | Agree | With the icons work above: step 9 shows the icon in its text and highlights it on Utilize. |
| 10 | Explain undo | Agree | Step 10's More (or a step after it): you can undo your moves until something new is revealed (a card drawn, a card turned over); moves that can't be undone show 🔒 and ask first. |
| 12 | Ships with a majority keep enemy Away Teams out | Agree, with the exact rule, kept short (there is no opponent here) | Step 13's More: an opponent can't send Away Teams to a Location where you have more Ships than they do (KW-SEND-03). Taught properly in the Bot tutorial. |
| 14 | Gaining also makes your deck bigger | Agree | Step 14: "…but every card gained makes your deck bigger and slower to get through, so gain cards you'll be glad to draw." |
| 15 | "You'll learn to return them" is awkward | Agree | Step 15: "Incidents are bad cards: −2 VP each at the end. Some cards return them to the Incident deck; you'll see one next turn." |
| 26 | Say a real game has no wipe here | Agree | Step 26: "Only practice games wipe a card at Clean-up; in a real game the Market is wiped when a Stardate runs out." |
| 29 | Define securing, and when it's controlled | Agree | Step 29: "A neutral Location is **secured** when you have 3+ tokens there and at least 2 more than your opponent. At the start of your next turn (the Control step) you may take control of one secured Location." The take-control procedure goes in step 46's More. |
| 39 | How a Duty Officer keeps working | Agree | Step 39: "He stays in play: his RESUPPLY gains you 1 Latinum at the start of every turn, and his Activations can be used once each turn." |
| 43 | Why discarding is usually right; did keeping Riker pay off? | Agree. And yes: Riker, kept in turn 1, was used in turn 2 (his PLAY took Utilize and Recruit back and sent the third Away Team, then he became Duty Officer) | Steps 28, 43, 62: "Discarding is usually good: you draw fresh cards, and your deck cycles sooner toward Reserve and Development cards. Keep a card only when you know how you'll use it next turn." Steps 28 and 43 then say what each kept card is for. |
| 44 | The kinds of cards: yours, Market, Reserve, Development | Agree | Step 44, with More: **starting deck** (your 10 cards), **Market** (gained into your deck), **Reserve** (Picard's 4 better cards, one joins your deck at each reshuffle), **Development** (his best cards, once the Reserve is empty, for a cost). |
| — | Resupply happens every turn, even with nothing to do | Agree | A short step at the start of turn 2: "Each turn starts with Resupply and Control. You have no RESUPPLY cards or secured Locations yet, so they passed by." |
| 46 | Dismiss, and why the Enterprise-D stayed away | Agree | Step 46: "Taking control **dismisses** every Ship there: it goes to your Discard pile with every card beamed to it. We kept the Enterprise-D away to protect the Allies on it, which Picard's mission needs." |
| 51 | The Glory comes with the card | Agree | Step 51: "Gain Halkan Council: its 2 Glory comes with it." |
| 56 | What "free" means | Agree | Step 56: "Its second effect has no Action icon, so it doesn't use an action: it's **free**." Step 10 gets the same wording. |
| 58 | The mission explained properly | Agree | Step 58: "**Peace Negotiations** is Picard's mission, the goal his deck is built around. Claim it once you have 3 Allies on one Ship and two tracks at 4: you gain 4 Dilithium and 4 cards." More: "Completing a mission also makes your **Focus** cards score at the end (each track's best multiplier × its Focus cards), so climbing the tracks pays twice." |
| Tip | Encounters are the best cards | Mostly agree | "Encounters are among the strongest cards in the game: one-off effects you take into your hand." |
| Tip | Developments | Kept as is | (You liked it.) |
| Tip | Final scoring misses the special VP | Agree | Lists every part: Glory, tokens on neutral Locations, **ENDGAME** abilities (Picard: 1 VP per Ally; some Locations score too), printed VP (Incidents −2), and **Focus** multipliers if you completed a mission. |

### Effect on length

About 6 new steps (turn 2's Resupply note, undo, the Burn is in More, the card kinds) and longer text on about 20 others. With More and the sheet, the main path grows to roughly 69 steps of the same short size.

### Steps

1. ✅ **Script text** (for your review again): every change in the table, the More texts, and the How cards work sheet's text. The replay test keeps proving the moves.
2. ✅ **Icons**: crop them from the rulebook pages, add them to the image set, and draw `[Action]`-style tokens as icons in the coach and card panels.
3. ✅ **More and the ? sheet** in the coach, on phone and laptop.
4. **Check and deploy**: ✅ the Playwright pass over every step on phone and laptop (text and icons shown, target visible, More opens, the ? sheet opens); deploy when you say so.
