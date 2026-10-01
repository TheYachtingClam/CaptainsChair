---
id: cb-rebner-advanced
captain: rebner
side: advanced
scan: cb-rebner-advanced.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 3
tracks:
  research: {}
  influence: {}
  military: {3: 1, 6: 2, 9: 3, 12: 4, 15: 5}
missions:
  - id: things-that-make-us-smart
    name: Things That Make Us Smart
    vp: 3
  - id: things-that-make-us-strong
    name: Things That Make Us Strong
    vp: 1
  - id: things-that-make-us-fast
    name: Things That Make Us Fast
    vp: 3
---

# Rebner: Advanced side

## Turn summary

The same as the Basic side: Control max 1, Actions 3. The Advanced side has no room to print it.

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Influence |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Military |  |  |  | ×1 |  |  | ×2 |  |  | ×3 |  |  | ×4 |  |  | ×5 |

Spaces before the first multiplier score ×0 for Focus icons.

## Missions

### Things That Make Us Smart (3 VP)

- **Printed goal:** Have an Engineer, a Scientist, and a Communication in play.
- **Goal check:** You have in play a card with Engineer, a card with Scientist and a card with Communication; one card may cover several.
- **Printed reward:** Enlist a Development reducing the cost by 1 [Dilithium] or 1 [Latinum]. If none of the contributing cards are Pakled, gain 2 [Glory].
- **Reward steps:**
  1. Enlist a Development, paying 1 less Dilithium or 1 less Latinum of its cost.
  2. If none of the cards that met the goal has Pakled, gain 2 Glory.
- **Actions used:** `ENLIST_DEVELOPMENT`, `GAIN_RESOURCE`
- **Undoable:** yes

### Things That Make Us Strong (1 VP)

- **Printed goal:** Have 2 Weapon in play, and [Military] at 6+.
- **Goal check:** 2 or more Weapon cards in play, and Military 6 or more.
- **Printed reward:** Scan for a [Military Focus]. Draw 3 cards.
- **Reward steps:**
  1. Scan for a card with a Military Focus icon.
  2. Draw 3 cards.
- **Actions used:** `SCAN_FOR`, `DRAW`
- **Undoable:** no

### Things That Make Us Fast (3 VP)

- **Printed goal:** Have 4 Ship deployed, and have at least 8 [Dilithium].
- **Goal check:** 4 or more deployed Ships, and 8 or more Dilithium in your pool.
- **Printed reward:** Draw the top Location and take control of it.
- **Reward steps:**
  1. Take control of the top card of the Location deck.
- **Actions used:** `TAKE_CONTROL`
- **Undoable:** no

## Rulings and open questions

- Research and Influence have no multipliers (REQ-CD-REB-02).

## Tests

- Given the goal is met, then the mission can be completed and its Mission Completion token placed (REQ-MS-06).
