# 07 – Turn Step 4: Clean-up Step and Stardates

Source: Rulebook pp. 12–13.

The Clean-up Step has these substeps, in order:
**Clean-up Operations → Stardate Resolution → Glory Placement → Discard, Draw & Refresh.**

## 1. Clean-up operations

- **REQ-CU-01** Trigger every **CLEAN-UP** operation the player has in play, in the player's chosen order.
  - Beamed cards are excluded.
  - Cards in the Staging Area are **included**.
- **REQ-CU-02** Effects are mandatory unless stated "may".

## 2. Emptying a Stardate card

This can happen at any time during a turn, not only during Clean-up.

- **REQ-SD-01** Any Glory gained is taken from the topmost Stardate card.
- **REQ-SD-02** When gaining Glory empties a Stardate card:
  1. Execute its "**When emptied**" effect immediately. Usually this gives the card to the **inactive** player, who places it in their Staging Area.
  2. Fill the new topmost Stardate card with the number of Glory printed on it, from the supply.
  3. Continue taking any remaining Glory owed from the new card.
- **REQ-SD-03** The received Stardate card stays in the receiving player's Staging Area until the Stardate Resolution substep of **their** next Clean-up Step.
- **REQ-SD-04 Final Stardate.** When the final Stardate card empties, it is not given to the inactive player and not refilled. This triggers the **Resolution** (see [01-game-overview.md](01-game-overview.md)). Further Glory comes from the supply.

## 3. Stardate Resolution

- **REQ-SD-10** If the player received a Stardate card during the opponent's previous turn, resolve its "**Stardate Resolution**" effect now. Then return that Stardate card to the box.
- **REQ-SD-11 Wipe the Market.**
  1. Return all resource tokens on Market cards to the supply.
  2. Move all 4 Market cards to the Junk pile.
  3. Reveal a replacement for each wiped card, if possible.
- **REQ-SD-12 Wipe the Neutral Zone** (only if the card says so).
  - Remove from the game every neutral Location that has **no tokens** (no Ships, no Away Teams).
  - Draw replacements from the Location deck.
  - Locations with one or more tokens stay.
  - Locations are never junked; they are removed from the game.
- **REQ-SD-13** The Market and Neutral Zone refill immediately, before the next substep.

## 4. Glory placement

- **REQ-CU-10** Take 1 Glory from the current Stardate card and place it on any one of the four Market cards. A card may hold any number of tokens.
- **REQ-CU-11** If this empties the Stardate, handle it as in §2. The card goes to the other player.
- **REQ-CU-12** After a Resolution, take the Glory from the supply instead.
- **REQ-CU-13** Tokens on a Market card are gained by the player who gains that card. See [08-cards-and-deck-management.md](08-cards-and-deck-management.md).

## 5. Discard, draw and refresh

- **REQ-CU-20 Discard.**
  - Move all cards from the Staging Area to the Discard pile.
  - The player **may** discard any number of cards from hand.
  - Location Area and Fleet Area cards, and Duty Officers, stay in play.
- **REQ-CU-21 Draw to hand size.** Draw until the hand has as many cards as the current hand size (normally 5).
  - If the hand already has that many or more, draw none and discard none.
  - There is no hand limit.
  - If the Draw deck runs out, apply Deck Cycling ([08-cards-and-deck-management.md](08-cards-and-deck-management.md)).
- **REQ-CU-22 Refresh.** Refresh all exhausted cards in play: Captain, Duty Officer(s), deployed Ships, controlled Locations, etc.
- **REQ-CU-23 Reset actions.** Reset Action tokens so the player has exactly 3 on the available side. Return any extra tokens gained during the turn to the supply.

## 6. Special operations

- **REQ-CU-30** Some cards have **SPECIAL** operations that state when they resolve, usually where a Passive would not work. The engine must support custom timing hooks for them.
