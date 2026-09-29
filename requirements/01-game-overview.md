# 01 – Game Overview, Resources & Win Conditions

Source: Rulebook pp. 1, 8 (*Star Trek: Captain's Chair – To Boldly Go*).

## 1. Product summary

- **REQ-OV-01** The application implements *Star Trek: Captain's Chair*, an asymmetric, thematic deck-building game.
- **REQ-OV-02** Each player plays as a famous captain with a unique Crew deck. Players recruit allies, analyze lifeforms, survey or conquer neutral planets (Locations), and manage resources.
- **REQ-OV-03** Supported player counts: **1–2 players**. Two-player is the primary mode. Solo mode is played against an automated opponent (the "Bot"), see [22-solo-mode.md](22-solo-mode.md). Cadet Training is a simpler solo practice mode, see [16-solo-and-cadet-training.md](16-solo-and-cadet-training.md).
- **REQ-OV-06** The game supports optional expansions. The first is *Second Contact* ([21-expansion-second-contact.md](21-expansion-second-contact.md)).
- **REQ-OV-04** Expected play time is 60–120 minutes. The online version should support saving and resuming a game in progress.
- **REQ-OV-05** At the end of the game the player with the most Victory Points (VP) wins, unless the game ends by the Burn (see §3).

## 2. Rules precedence

- **REQ-OV-10** Where general rules and the "Keywords in Detail" rules disagree, the Keywords in Detail rules win. The rules engine must encode keyword behaviour from [14-keywords.md](14-keywords.md) as the authority.
- **REQ-OV-11** Where a card's text contradicts the general rules, the card's text applies (standard deck-builder convention; confirm per keyword).
- **REQ-OV-12** This rulebook ("To Boldly Go") supersedes the Core Box rulebook where they differ.

## 3. Game structure and end conditions

- **REQ-OV-20** Play alternates between the two players. The active player fully resolves all four turn steps before play passes.
- **REQ-OV-21** Turn steps, in order: **Resupply → Control → Action → Clean-up** (see [05-resupply-and-control.md](05-resupply-and-control.md), [06-action-step.md](06-action-step.md), [07-clean-up-step.md](07-clean-up-step.md)).
- **REQ-OV-22 Resolution (normal end).** When the last Stardate card empties, a Resolution is triggered.
  - Play continues until the second player (the one without the Starting Player token) finishes their turn.
  - Then both players take one more turn each.
  - Then the game proceeds to Final Scoring ([13-final-scoring.md](13-final-scoring.md)).
- **REQ-OV-23 The Burn (sudden end).** If the Incident deck is empty, the game ends immediately.
  - The player with fewer Incident cards wins. Count Incidents in hand, in play, in the Discard pile, in the Draw deck and in the Captain's Log. Do **not** count the Reserve deck.
  - On a tie, proceed to Final Scoring.
  - The Burn can trigger during the final turns after a Resolution. The Burn takes priority and ends the game immediately.
- **REQ-OV-24** The UI must clearly show when a Resolution has been triggered and how many turns remain.

## 4. Resources

- **REQ-RES-01** There are three resource types: **Dilithium**, **Latinum** and **Glory**.
- **REQ-RES-02** Gaining a resource moves tokens into the player's personal resource pool, or onto a specified card in play when the effect says so.
- **REQ-RES-03 Source of tokens.**
  - Latinum and Dilithium come from the general supply.
  - Glory comes from the **topmost Stardate card**.
  - After a Resolution has been triggered, Glory comes from the supply.
- **REQ-RES-04 Spending.** Spending returns tokens from the player's resource pool to the supply.
  - Resources on cards in play cannot be spent.
  - If a required cost cannot be paid, the operation cannot be resolved.
- **REQ-RES-05 Glory substitution.**
  - When spending Latinum, a player may instead spend any number of Glory, each worth 1 Latinum.
  - When spending Dilithium, a player may instead spend any number of Glory, each worth 2 Dilithium. No change is given.
  - No other conversions are allowed unless an effect permits it.
- **REQ-RES-06** Resource tokens, Action tokens and Glory are unlimited. The digital version must model them as unbounded counters (the physical "×5" tokens are only a display aid).
- **REQ-RES-07** Location cards are the usual source of resources, directly or via cards such as *Utilize*.

## 5. UI notes

- **REQ-OV-30** Show each player's resource pool (Dilithium, Latinum, Glory) and available Action tokens at all times.
- **REQ-OV-31** Provide an in-game keyword glossary and a turn-step indicator.
