---
id: cb-burnham-advanced
captain: burnham
side: advanced
scan: cb-burnham-advanced.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 3
tracks:
  research:  {2: 1, 7: 2, 10: 3, 13: 4, 15: 5}
  influence: {2: 1, 7: 2, 10: 3, 13: 4, 15: 5}
  military:  {5: 2, 10: 3, 14: 4}
missions:
  - id: investigate-the-burn
    name: "Investigate the Burn"
    vp: 4
  - id: reunite-the-federation
    name: "Reunite the Federation"
    vp: 3
  - id: dealing-with-the-emerald-chain
    name: "Dealing with the Emerald Chain"
    vp: 6
---

# Burnham: Advanced side

## Turn summary

The same as the Basic side: Control max 1, Actions 3. The Advanced side has no room to print it.

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research |  |  | ×1 |  |  |  |  | ×2 |  |  | ×3 |  |  | ×4 |  | ×5 |
| Influence |  |  | ×1 |  |  |  |  | ×2 |  |  | ×3 |  |  | ×4 |  | ×5 |
| Military |  |  |  |  |  | ×2 |  |  |  |  | ×3 |  |  |  | ×4 |  |

## Missions

### Investigate the Burn (4 VP)

Same goal and reward as the Basic side; see [cb-burnham-basic.md](cb-burnham-basic.md).

- **Actions used:** `TAKE_ENCOUNTER`, `MOVE_RESOURCES`
- **Undoable:** no

### Reunite the Federation (3 VP)

- **Printed goal:** Have an Anomaly logged. Have 3 Starfleet in play (excluding your Captain). Have 3 Different Species (excluding cards with Starfleet) on the same Ship.
- **Goal check:** an Anomaly card in your Log; 3 or more Starfleet cards in play besides your Captain; and one deployed Ship whose non-Starfleet beamed cards show 3 or more different Species traits.
- **Printed reward:** Draw the top Location and take control of it.
- **Reward steps:**
  1. Take the top card of the Location deck and take control of it.
- **Actions used:** `TAKE_CONTROL`
- **Undoable:** no

### Dealing with the Emerald Chain (6 VP)

- **Printed goal:** Have 2 Business/Orion in play. Have 2 Shady logged.
- **Goal check:** 2 or more cards in play that are Business or Orion; and 2 or more Shady cards in your Log.
- **Printed reward:** You *may* free play an Incident to gain 2 [Glory], 2 [Dilithium], and 2 [Latinum].
- **Reward steps:**
  1. You may free play an Incident. If you do, gain 2 Glory, 2 Dilithium and 2 Latinum.
- **Actions used:** `FREE_PLAY`, `GAIN_RESOURCE`
- **Undoable:** yes

## Rulings and open questions

- The Dilithium gained goes onto Inert Dilithium while that card is in play.
- Ruling (confirmed 2026-10-10): for *Reunite the Federation*, the 3 different Species are counted on the Ship card and the cards beamed to it, leaving out cards with Starfleet.

## Tests

- Given the goal of Reunite the Federation is met, when the mission is completed, then its reward resolves.
- Given the goal of Dealing with the Emerald Chain is met, when the mission is completed, then its reward resolves.
