---
id: cb-shran-basic
captain: shran
side: basic
scan: cb-shran-basic.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 1
tracks:
  research:  {0: 1, 5: 3, 10: 4, 14: 5}
  influence: {0: 1, 2: 2, 7: 3, 10: 4, 13: 5, 15: 6}
  military:  {0: 1, 3: 2, 8: 3, 11: 5, 15: 6}
missions:
  - id: securing-andorias-borders
    name: "Securing Andoria's Borders"
    vp: null
---

# Shran: Basic side

## Turn summary

1. Resupply
2. Control (max 1)
3. Actions (3)
4. Clean-up: A. Resolve Stardate, B. Place Glory, C. Discard & Draw

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research | ×1 |  |  |  |  | ×3 |  |  |  |  | ×4 |  |  |  | ×5 |  |
| Influence | ×1 |  | ×2 |  |  |  |  | ×3 |  |  | ×4 |  |  | ×5 |  | ×6 |
| Military | ×1 |  |  | ×2 |  |  |  |  | ×3 |  |  | ×5 |  |  |  | ×6 |

## Missions

### Securing Andoria's Borders

- **Printed goal:** Have 3 controlled Location in play, and 4 Weapon in play.
- **Goal check:** 3 or more Locations under your control; and 4 or more Weapon cards in play.
- **Printed reward:** Scan 1 of Ship, draw a card, gain an [Action].
- **Reward steps:**
  1. Scan 1 of Ship.
  2. Draw a card.
  3. Gain an action.
- **Actions used:** `SCAN`, `DRAW`, `GAIN_ACTION`
- **Undoable:** no
- **VP:** none on the Basic side.

## Rulings and open questions

None.

## Tests

- Given the goal of Securing Andoria's Borders is met, when the mission is completed, then its reward resolves.
