---
id: cb-picard-basic
captain: picard
side: basic
scan: cb-picard-basic.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 1
tracks:
  research:  {0: 1, 2: 2, 7: 3, 10: 4, 13: 5, 15: 6}
  influence: {0: 1, 3: 2, 8: 3, 11: 5, 15: 7}
  military:  {0: 1, 5: 3, 10: 4, 14: 5}
missions:
  - id: peace-negotiations
    name: "Peace Negotiations"
    vp: null
---

# Picard: Basic side

## Turn summary

1. Resupply
2. Control (max 1)
3. Actions (3)
4. Clean-up: A. Resolve Stardate, B. Place Glory, C. Discard & Draw

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research | ×1 |  | ×2 |  |  |  |  | ×3 |  |  | ×4 |  |  | ×5 |  | ×6 |
| Influence | ×1 |  |  | ×2 |  |  |  |  | ×3 |  |  | ×5 |  |  |  | ×7 |
| Military | ×1 |  |  |  |  | ×3 |  |  |  |  | ×4 |  |  |  | ×5 |  |

## Missions

### Peace Negotiations

- **Printed goal:** have 3 Ally on the same Ship, and at least two of [Military]/[Influence]/[Research] at 4+.
- **Goal check:** one deployed Ship with 3 or more Allies beamed to it (REQ-MS-03); and at least two of the three tracks at 4 or more.
- **Printed reward:** Gain 4 [Dilithium] and draw 4 cards. You *may* junk a card from the Market.
- **Reward steps:**
  1. Gain 4 Dilithium.
  2. Draw 4 cards.
  3. You may junk a card from the Market.
- **Actions used:** `GAIN_RESOURCE`, `DRAW`, `JUNK`
- **Undoable:** no
- **VP:** none on the Basic side.

## Rulings and open questions

- The beamed Allies that met the goal are dismissed afterwards (REQ-MS-06).

## Tests

- Given the goal of Peace Negotiations is met, when the mission is completed, then its reward resolves.
