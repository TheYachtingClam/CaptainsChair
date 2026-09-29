# 05 – Turn Steps 1 & 2: Resupply and Control

Source: Rulebook p. 9.

## 1. Resupply Step

- **REQ-RS-01** At the start of the turn, trigger every **RESUPPLY** operation the active player has in play.
  - Beamed cards (tucked behind other cards) are excluded.
  - The player chooses the order.
- **REQ-RS-02** All effects are mandatory unless the text says "may".
- **REQ-RS-03** Some Resupply operations are repeatable, for example "Repeat this for each Ongoing you have in play". The player sees each result before deciding on the next optional repetition.
- **REQ-RS-04** The UI should list pending Resupply operations and let the player pick the order. If only mandatory, order-independent effects exist, the engine may auto-resolve them.

## 2. Control Step

- **REQ-CT-01 Secured.** A neutral Location (in the Neutral Zone) is **secured** by a player when that player has **at least 3 tokens** there and **at least 2 more tokens than the opponent**. Tokens are Ship tokens and Away Team tokens in any combination.
- **REQ-CT-02** During the Control Step the active player **may** take control of **one** secured neutral Location.
- **REQ-CT-03 Take-control procedure:**
  1. The opponent gains 1 Glory for each of their tokens (Away Team or Ship) at that Location.
  2. All Away Teams at that Location, from both players, return to their owners' Captain cards.
  3. All Ships at that Location, from both players, are **dismissed**. Their cards go to their owners' Discard piles and their tokens return to the supply.
  4. Move the Location card from the Neutral Zone to the active player's Location Area.
  5. Immediately resolve its **CONTROL** operation.
  6. Refill the Neutral Zone to three by revealing the next Location deck card, if possible.
- **REQ-CT-04** A Location's **RESUPPLY** operation does not trigger on the turn control was taken, because the Resupply Step has passed. It triggers from the next turn.
- **REQ-CT-05** Some crew boards or cards raise the per-turn control limit (the turn summary on Crew boards shows "CONTROL (MAX: 1)"). The engine must read the limit from the board and from effects.
- **REQ-CT-06** The UI should highlight Locations the active player has secured, and show token counts per player on each Neutral Zone Location.
