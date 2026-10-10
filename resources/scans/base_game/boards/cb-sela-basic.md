---
id: cb-sela-basic
captain: sela
side: basic
scan: cb-sela-basic.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 1
tracks:
  research:  {0: 1, 5: 3, 10: 4, 14: 5}
  influence: {0: 1, 5: 3, 10: 4, 14: 5}
  military:  {0: 1, 5: 3, 10: 4, 14: 5}
missions:
  - id: romulan-might
    name: "Romulan Might"
    vp: null
---

# Sela: Basic side

## Turn summary

1. Resupply
2. Control (max 1)
3. Actions (3)
4. Clean-up: A. Resolve Stardate, B. Place Glory, C. Discard & Draw

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research | ×1 |  |  |  |  | ×3 |  |  |  |  | ×4 |  |  |  | ×5 |  |
| Influence | ×1 |  |  |  |  | ×3 |  |  |  |  | ×4 |  |  |  | ×5 |  |
| Military | ×1 |  |  |  |  | ×3 |  |  |  |  | ×4 |  |  |  | ×5 |  |

## Missions

### Romulan Might

- **Printed goal:** Have [Influence] at 6+ and [Military] at 6+.
- **Goal check:** Influence track 6 or more and Military track 6 or more.
- **Printed reward:** Enlist a Development. Find an Attack.
- **Reward steps:**
  1. Enlist a Development, paying its cost.
  2. Find an Attack card.
- **Actions used:** `ENLIST_DEVELOPMENT`, `FIND`
- **Undoable:** no
- **VP:** none on the Basic side.

## Rulings and open questions

- Ruling (confirmed 2026-10-10): for *Romulan Might*, enlisting a Development still costs its development cost.

## Tests

- Given the goal of Romulan Might is met, when the mission is completed, then its reward resolves.
