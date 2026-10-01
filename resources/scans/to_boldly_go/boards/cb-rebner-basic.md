---
id: cb-rebner-basic
captain: rebner
side: basic
scan: cb-rebner-basic.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 1
tracks:
  research: {}
  influence: {}
  military: {0: 1, 3: 2, 6: 3, 9: 4, 12: 5, 15: 6}
missions:
  - id: things-that-make-us-smart
    name: Things That Make Us Smart
    vp: null
---

# Rebner: Basic side

## Turn summary

1. Resupply
2. Control (max 1)
3. Actions (3)
4. Clean-up: A. Resolve Stardate, B. Place Glory, C. Discard & Draw

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Influence |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Military | ×1 |  |  | ×2 |  |  | ×3 |  |  | ×4 |  |  | ×5 |  |  | ×6 |

## Missions

### Things That Make Us Smart

- **Printed goal:** Have an Engineer, a Scientist, and a Communication in play.
- **Goal check:** You have in play a card with Engineer, a card with Scientist and a card with Communication; one card may cover several.
- **Printed reward:** Enlist a Development reducing the cost by 1 [Dilithium] or 1 [Latinum]. If none of the contributing cards are Pakled, gain 2 [Glory].
- **Reward steps:**
  1. Enlist a Development, paying 1 less Dilithium or 1 less Latinum of its cost.
  2. If none of the cards that met the goal has Pakled, gain 2 Glory.
- **Actions used:** `ENLIST_DEVELOPMENT`, `GAIN_RESOURCE`
- **Undoable:** yes
- **VP:** none on the Basic side.

## Rulings and open questions

- Research and Influence have no multipliers at all on either side, matching REQ-CD-REB-02: those tracks only meet requirements.
- The engine must remember which cards met the goal, for the Pakled check.

## Tests

- Given the goal is met, then the mission can be completed and its Mission Completion token placed (REQ-MS-06).
