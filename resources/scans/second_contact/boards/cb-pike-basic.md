---
id: cb-pike-basic
captain: pike
side: basic
scan: cb-pike-basic.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 1
tracks:
  research: {0: 1, 9: 4, 14: 5}
  influence: {0: 1, 5: 3, 10: 4, 15: 6}
  military: {0: 1, 3: 2, 5: 3, 9: 4}
missions:
  - id: weight-of-the-future
    name: Weight of the Future
    vp: null
---

# Pike: Basic side

## Turn summary

1. Resupply
2. Control (max 1)
3. Actions (3)
4. Clean-up: A. Resolve Stardate, B. Place Glory, C. Discard & Draw

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research | ×1 |  |  |  |  |  |  |  |  | ×4 |  |  |  |  | ×5 |  |
| Influence | ×1 |  |  |  |  | ×3 |  |  |  |  | ×4 |  |  |  |  | ×6 |
| Military | ×1 |  |  | ×2 |  | ×3 |  |  |  | ×4 |  |  |  |  |  |  |

## Missions

### Weight of the Future

- **Printed goal:** Have 4 Time Travel in play (excluding your Captain) and 2 deployed Ongoing.
- **Goal check:** 4 or more Time Travel cards in play, not counting Christopher Pike; and 2 or more deployed Ongoing cards.
- **Printed reward:** Up to twice, return an Incident from your hand, Discard pile, or Log. For each Incident returned this way, draw a card.
- **Reward steps:**
  1. Up to twice: return an Incident from your hand, Discard pile or Log, then draw a card.
- **Actions used:** `RETURN_INCIDENT`, `DRAW`
- **Undoable:** no
- **VP:** none on the Basic side.

## Rulings and open questions

- Pike's tracks skip many multipliers, as printed: Research ×1, ×4, ×5; Influence ×1, ×3, ×4, ×6; Military ×1, ×2, ×3, ×4.

## Tests

- Given the goal is met, then the mission can be completed and its Mission Completion token placed (REQ-MS-06).
