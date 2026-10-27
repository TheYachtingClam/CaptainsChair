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

### Step 2: Stacked setup and the tutorial on the server

- `new_game(..., stack=…)`; the tutorial's setup stored with the game.
- `app/tutorial.py`, the `tutorial` view block, move filtering, and an endpoint to start a tutorial game.
- Tests: the scripted moves replay to the end of turn 3 with the stacked decks; a move the step does not allow is refused; undo goes back a step; the stacking does not change ordinary games.

**You test:** start the tutorial through the API and step through it with the existing table (no coach yet).

### Step 3: The coach on the table

- The coach panel and spotlight, on a laptop and on a phone (a block in the bottom sheet; switches tabs).
- `data-tutorial` targets on the table's cards, zones and buttons; moves the step does not allow are greyed out.
- Next, Back, "Let me play", Leave tutorial.

**You test:** play the scripted turns on your phone and laptop.

### Step 4: Free play, tips and the end

- Tips that wait for an event or a kind of decision, each shown once.
- The end: final scoring explained line by line, the Cadet rating, and "Play against a Bot next".
- The lobby's "Learn to play" card and Tutorials list; the account remembers a finished tutorial.

**You test:** play the whole tutorial to the end.

### Step 5: Test pass and deploy

- A Playwright run through the whole tutorial on an emulated phone and a laptop (the player from the phone plan's Step 6, following the coach).
- Fixes from your play-through; deploy.

## Later tutorials

A new tutorial is a new YAML file: its setup (Captain, box, stacked decks, mode) and its steps. The framework's step kinds, tips and coach serve all of them. A tutorial that needs an opponent (attacks, contested Locations) uses solo mode against a Bot instead of Cadet Training; the script then also covers the Bot's turns.

## Risks and notes

- **The script must match the cards.** If a card's code or the rules change, a scripted move may no longer exist. The replay test in Step 2 fails when that happens, so it is caught before players see it.
- **Text length on a phone.** Each step's text is kept to two or three short sentences; longer explanations are split.
- **Rails that are too tight feel like a slideshow.** Only turns 1 to 3 are on rails, and "Let me play" is always there.
