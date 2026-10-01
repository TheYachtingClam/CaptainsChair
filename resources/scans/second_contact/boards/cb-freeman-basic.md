---
id: cb-freeman-basic
captain: freeman
side: basic
scan: cb-freeman-basic.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 1
tracks:
  research: {0: 1, 2: 2, 7: 3, 10: 4, 13: 5, 15: 6}
  influence: {0: 1, 2: 2, 7: 3, 10: 4, 13: 5, 15: 6}
  military: {0: 1, 2: 2, 7: 3, 10: 4, 13: 5, 15: 6}
missions:
  - id: project-swing-by
    name: Project Swing By
    vp: null
---

# Freeman: Basic side

## Turn summary

1. Resupply
2. Control (max 1)
3. Actions (3)
4. Clean-up: A. Resolve Stardate, B. Place Glory, C. Discard & Draw

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research | ×1 |  | ×2 |  |  |  |  | ×3 |  |  | ×4 |  |  | ×5 |  | ×6 |
| Influence | ×1 |  | ×2 |  |  |  |  | ×3 |  |  | ×4 |  |  | ×5 |  | ×6 |
| Military | ×1 |  | ×2 |  |  |  |  | ×3 |  |  | ×4 |  |  | ×5 |  | ×6 |

## Missions

### Project Swing By

- **Printed goal:** Have 4 Ally on the same Ship, and at least two of [Military]/[Influence]/[Research] at 4+.
- **Goal check:** One deployed Ship, with its beamed cards, has 4 or more Allies (REQ-MS-03); and at least 2 of your 3 tracks are at 4 or more.
- **Printed reward:** Gain 4 [Dilithium] and draw 4 cards. You *may* junk a card from the Market.
- **Reward steps:**
  1. Gain 4 Dilithium.
  2. Draw 4 cards.
  3. You may junk a Market card.
- **Actions used:** `GAIN_RESOURCE`, `DRAW`, `JUNK`
- **Undoable:** no
- **VP:** none on the Basic side.

## Rulings and open questions

- The beamed Allies that met the goal are dismissed on completion (REQ-MS-06).

## Tests

- Given the goal is met, then the mission can be completed and its Mission Completion token placed (REQ-MS-06).
