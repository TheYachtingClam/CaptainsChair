# 20 – Undo

Undo is part of the first version. This file defines what a player can undo, how the game warns them before a move that cannot be undone, and how the server implements it. It builds on the command log in [19-technical-architecture.md](19-technical-architecture.md) §3.3.

## 1. Why undo needs rules

A free undo button would let a player cheat in two ways:

- **Peeking.** Draw a card, see it, undo, and play differently with that knowledge.
- **Re-rolling.** Undo a shuffle or a reveal and try again for a better result.

So some moves can never be undone. Instead of letting players ask for exceptions, the game **warns the player before every move that cannot be undone**, and they confirm it or back out.

## 2. Definitions

- **Command.** One player input accepted by the server, such as playing a card or choosing a target (REQ-SRV-11).
- **Irreversible command.** A command that, once applied, can never be undone (§3).
- **Checkpoint.** The point right after an irreversible command. Undo cannot go back past it.

## 3. Irreversible commands

- **REQ-UNDO-01** A command is irreversible if applying it does any of the following:
  1. **Reveals hidden information to anyone.** Examples: drawing a card, looking at or revealing cards from any deck (scan, find, gain the top card of a Market deck, refill the Market or Neutral Zone), taking an Incident or Encounter.
  2. **Uses randomness.** Examples: shuffling any deck, including a reshuffle when the Draw deck runs out.
  3. **Hands a decision to the opponent.** Examples: a forced effect where the opponent chooses, offering the opponent a Reaction, resolving an attack's negative effect against them.
  4. **Ends the turn.**
- **REQ-UNDO-02** Any answer the non-active player gives on the opponent's turn, such as using or declining a Reaction, is irreversible.
- **REQ-UNDO-03** The server decides which commands are irreversible. The rules engine marks each event it produces as revealing, random, involving the opponent, or none. The engine's tests must check these markings for every keyword in [14-keywords.md](14-keywords.md).
- **REQ-UNDO-04** The start of each turn is always a checkpoint.

## 4. Knowing in advance

The warning must appear **before** the command is sent, so the client has to know which choices are irreversible.

- **REQ-UNDO-10** Every legal option in a pending decision (REQ-SRV-12) carries an `irreversible` flag and, when true, a short reason such as "You will draw a card" or "Your opponent will choose".
- **REQ-UNDO-11** To set the flag, the engine checks whether applying that option would reach an irreversible event before the next player decision. It does this by simulating the option on a copy of the state, without revealing the result to anyone.
- **REQ-UNDO-12** If the result depends on something the engine cannot know without revealing hidden information, the engine flags the option as irreversible. It is better to warn unnecessarily than to miss a warning.
- **REQ-UNDO-13** The server re-checks on receipt. If a command marked reversible turns out to be irreversible, the server applies it anyway and logs the mismatch as a bug for developers.

## 5. The warning

- **REQ-UNDO-20** When the player picks an option flagged irreversible, the client shows a confirmation **every time**, before sending anything:
  - Title: "This can't be undone"
  - The reason from REQ-UNDO-10, for example "You will draw 2 cards."
  - Buttons: **Continue** and **Go back**.
- **REQ-UNDO-21** **Go back** sends nothing and returns the player to the same choice.
- **REQ-UNDO-22** The warning applies to both players, including the non-active player answering a prompt on the opponent's turn.
- **REQ-UNDO-23** Ending the turn always shows the warning, even if nothing else would be revealed.
- **REQ-UNDO-24** Pressing Enter confirms **Continue**; Escape confirms **Go back**. Focus starts on **Go back**, so a stray key press cannot confirm by accident.

## 6. Undo

- **REQ-UNDO-30** During their own turn, the active player may undo their most recent command, as long as it is not irreversible and no checkpoint lies after it.
- **REQ-UNDO-31** They may repeat this, one command at a time, back to the most recent checkpoint.
- **REQ-UNDO-32** Examples of moves that can usually be undone:
  - Spending resources, placing an Action token.
  - Choosing which PLAY operation to resolve, before it reveals anything.
  - Warping a Ship, sending an Away Team, promoting a Person from hand, beaming a card.
  - Moving Glory to a Market card during Glory Placement.
  - Choosing the order of Resupply or Clean-up operations.
- **REQ-UNDO-33** A player cannot undo anything during the opponent's turn.
- **REQ-UNDO-34** There is no way to undo past a checkpoint, and no request or approval mechanism. The warning is the protection.

## 7. What happens on undo

- **REQ-UNDO-40** Undo restores the full game state to the chosen point: every zone, token, resource, track, Stardate, exhausted card, Action token and pending decision.
- **REQ-UNDO-41** Undone commands are kept in the history, marked as undone, for debugging. They are never replayed.
- **REQ-UNDO-42** Both players' views update at once. The action log shows "*Name* undid: *summary*".
- **REQ-UNDO-43** After the game ends and scoring is shown, nothing can be undone.

## 8. Randomness and replay

- **REQ-UNDO-50** The random generator's state is part of the game state. Restoring a point in history restores the generator exactly as it was.
- **REQ-UNDO-51** Undo is implemented by restoring the stored state at the target point, or by replaying accepted commands from the last snapshot. The result must equal the original state exactly. Tests must check this for every acceptance scenario in [18-acceptance-scenarios.md](18-acceptance-scenarios.md).
- **REQ-UNDO-52** The server stores a state snapshot at every checkpoint, so undo does not need to replay the whole game.

## 9. Cadet Training mode

- **REQ-UNDO-60** Cadet Training ([16-solo-and-cadet-training.md](16-solo-and-cadet-training.md)) uses exactly the same undo rules and warnings as normal play. Nothing in this file has a Cadet Training exception.
- **REQ-UNDO-61** Moves that would involve the opponent in normal play, such as effects against the virtual opponent, follow the same rules as any other move: they are final only if they reveal information, use randomness or end the turn.

## 10. API

| Method and path | Purpose |
|---|---|
| `POST /api/games/{id}/undo` | Undo the last command |

- **REQ-UNDO-70** Each player view says whether undo is available and, if so, gives a short description of the command it would undo.
- **REQ-UNDO-71** Undo is also available over the game WebSocket.

## 11. Client

- **REQ-UNDO-80** The game table has an **Undo** button, also bound to Ctrl+Z / Cmd+Z. It is enabled only when undo is available. Its tooltip names the command it will undo, for example "Undo: warp U.S.S. Shenzhou to Archer IV".
- **REQ-UNDO-81** Options flagged irreversible get a small marker, such as a lock icon, so the player can see which moves are final before choosing.
- **REQ-UNDO-82** The action log marks checkpoints, so players can see how far back undo reaches.
