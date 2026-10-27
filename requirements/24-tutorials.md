# 24 – Tutorials

A tutorial is a real game with a coach: it explains each part of *Captain's Chair* as it comes up, points at the card, zone or button involved, and for its first turns allows only the move it asks for. The plan is [plans/tutorial.md](../plans/tutorial.md).

## 1. The framework

### 1.1 Tutorials are data

- **REQ-TUT-01** A tutorial is a script file, `server/content/tutorials/<id>.yaml`, with an id, a title, a one-line summary, its setup (§1.2), its steps (§1.3) and its tips (§1.4). Adding a tutorial adds a file, not code.
- **REQ-TUT-02** A tutorial game is an ordinary game of its mode (Cadet Training for the first tutorial) with a `tutorial` field naming the script. Everything else (replay from seed and moves, undo, the can't-be-undone warning, bug reports) works as in any game.

### 1.2 Setup

- **REQ-TUT-10** The setup names the mode, box, Crew deck, board side and seed, and may **stack** the decks: the player's starting hand and Draw deck in order, the Reserve deck, a Market slot's face-up card, the order of the top cards of a Market deck, the three Neutral Zone Locations, and the top of the Incident deck. Unnamed cards keep the order the seed gives them.
- **REQ-TUT-11** Stacking happens once, at setup. Later shuffles (a deck cycling) follow the seed, so they are the same every time the tutorial is played.
- **REQ-TUT-12** The stacked setup is stored with the game, so rebuilding it from the seed and moves gives the same game.

### 1.3 Steps

- **REQ-TUT-20** A step has an id and the coach's text (`say`: two or three short sentences, with **bold** for card and game terms). It may point at something (`show`) and either wait for a move (`expect`) or wait for the player to tap Next (`next: button`).
- **REQ-TUT-21** `show` names one of: a card (`card:<card id>`, the instance the player owns, or in the Market or Neutral Zone), a zone (`zone:hand`, `zone:resources`, `zone:tracks`, `zone:captain`, `zone:fleet`, `zone:locations`, `zone:duty`, `zone:staging`, `zone:discard`, `zone:deck`, `zone:reserve`, `zone:development`, `zone:log`, `zone:market`, `zone:market:<suit>`, `zone:neutral`, `zone:stardate`, `zone:incident`), a button (`button:end-turn`, `button:undo`, `button:next`) or the question in the bottom sheet (`question`). On a phone the coach switches to the tab that holds it.
- **REQ-TUT-22** `expect` is one move or a list of moves, written so that the script needs no card uids:
  - `play:<card id>:<n>` and `activate:<card id>:<n>`: play or activate that card's operation n;
  - `<card id>`: the answer that is that card (choosing a card to discard, warp to, beam, take back);
  - `pick:<suit>`: the answer that is a card of that suit (an Incident whose name the seed decides);
  - `take:<card id>`: take control of that Location;
  - anything else is the answer's own id (`end`, `done`, `yes`, `none`, `top`, `discard`, `beam`, `use:0`, `market:Ally`, `wipe:Ally`, `glory:Ally`).
- **REQ-TUT-23** While a step waits for a move (**on rails**), every other answer is shown but disabled, with the coach's text as the reason, and the server refuses it.
- **REQ-TUT-24** The current step is worked out from the game's moves: each expected move answered moves on one step, each Next tap is stored as a move of its own. Undo therefore also steps the coach back.
- **REQ-TUT-25** The rails end after the script's last step, or earlier when the player chooses **Let me play**; from then on the game is free and only tips appear (§1.4).

### 1.4 Tips

- **REQ-TUT-30** A tip has an id, the coach's text, what to show, and a trigger: an event (`event: take_incident`, `event: cycle`, …), a kind of question (`question: mission`, `question: develop`, …) or a game moment (`moment: stardate-empties`, `moment: resolution`, `moment: final-scoring`).
- **REQ-TUT-31** Each tip appears once per game, the first time its trigger holds after the rails end, and stays until the player taps **Got it** (stored like Next, so undo brings it back). It never blocks a move. One tip shows at a time, in the script's order. A tip may carry a link (the last one: Play against a Bot).
- **REQ-TUT-32** Triggers look at the game as it is: a question (`question: mission` when a mission can be claimed, `encounter` or `develop` by the question's words), a card that can be played (`playable: <card id>`), a track at a value (`track_at_least: n`), an Incident in hand (`event: take_incident`), or a moment (`stardate-empties`: the first Stardate is used up; `last-turn`; `final-scoring` and `game-over`: the game has ended).

### 1.5 The coach on screen

- **REQ-TUT-40** On a laptop the coach is a panel beside what it points at; on a phone it is the top block of the bottom sheet (REQ-CLI-34). It shows the text, Back (for explanations), Next where needed, progress ("Step 7 of 52"), **Let me play** and **Leave tutorial**.
- **REQ-TUT-41** What the step points at is highlighted and the rest of the table dimmed, without blocking it: cards can still be pressed and held to read them (REQ-CLI-31).
- **REQ-TUT-42** Leaving keeps the game; the lobby offers to continue it or start again.

### 1.6 The lobby and the account

- **REQ-TUT-50** The lobby shows a **Learn to play** card to an account that has not finished the first tutorial, and a **Tutorials** list with every tutorial and whether it is finished.
- **REQ-TUT-51** A tutorial is finished when its game reaches final scoring. The account remembers it.

## 2. The first tutorial: "Learn to play with Picard"

- **REQ-TUT-60** Cadet Training (REQ-CTM-01 to -23) with Jean-Luc Picard's Core Box deck, Basic side, the Core Box only.
- **REQ-TUT-61** Turns 1 to 3 are on rails; turns 4 to 11 are free play with tips; the game ends with final scoring explained line by line and the Cadet rating.
- **REQ-TUT-62** It teaches, in this order: how to win; the table; the turn; playing cards and resources; the Market and gaining; Picard's Reaction; warping Ships; the Captain's Log; the Cadet Clean-up; drawing up and deck cycling with the Reserve; Away Teams and securing a Location; drawing from the Discard pile; Incidents and returning them; the Staging Area and promoting a Duty Officer; the Control step and taking control (and that it dismisses Ships there); Crew Locations; beaming to Ships and Picard's mission. Tips cover the rest: Encounters, Developments, Specialty tracks and the mission, the Stardate emptying, the Burn, logging, and final scoring.
- **REQ-TUT-63** Attacks and an opponent's turns are not taught here; the last step points the player at solo play against a Bot.
