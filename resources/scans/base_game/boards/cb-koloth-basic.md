---
id: cb-koloth-basic
captain: koloth
side: basic
scan: cb-koloth-basic.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 1
tracks:
  research:  {0: 1, 5: 3, 10: 4, 14: 5}
  influence: {0: 1, 3: 2, 8: 3, 11: 5, 15: 7}
  military:  {0: 1, 2: 2, 7: 3, 10: 4, 13: 5, 15: 7}
missions:
  - id: expanding-the-empire
    name: "Expanding the Empire"
    vp: null
---

# Koloth: Basic side

## Turn summary

1. Resupply
2. Control (max 1)
3. Actions (3)
4. Clean-up: A. Resolve Stardate, B. Place Glory, C. Discard & Draw

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research | ×1 |  |  |  |  | ×3 |  |  |  |  | ×4 |  |  |  | ×5 |  |
| Influence | ×1 |  |  | ×2 |  |  |  |  | ×3 |  |  | ×5 |  |  |  | ×7 |
| Military | ×1 |  | ×2 |  |  |  |  | ×3 |  |  | ×4 |  |  | ×5 |  | ×7 |

## Missions

### Expanding the Empire

- **Printed goal:** Have a total of 6 deployed Ship / controlled Location in play, at least one of each.
- **Goal check:** deployed Ships plus controlled Locations total 6 or more, with at least 1 Ship and 1 Location.
- **Printed reward:** Enlist two Reserves **OR** Enlist a Development. Dismiss a deployed Ship.
- **Reward steps:**
  1. Choose: enlist 2 Reserves, or enlist a Development (paying its cost).
  2. Dismiss one of your deployed Ships.
- **Actions used:** `ENLIST_RESERVE`, `ENLIST_DEVELOPMENT`, `DISMISS`
- **Undoable:** yes
- **VP:** none on the Basic side.

## Rulings and open questions

None.

## Tests

- Given the goal of Expanding the Empire is met, when the mission is completed, then its reward resolves.
