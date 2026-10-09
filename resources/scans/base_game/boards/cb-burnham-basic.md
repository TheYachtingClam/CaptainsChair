---
id: cb-burnham-basic
captain: burnham
side: basic
scan: cb-burnham-basic.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 1
tracks:
  research:  {0: 1, 2: 2, 7: 3, 10: 4, 13: 5, 15: 6}
  influence: {0: 1, 2: 2, 7: 3, 10: 4, 13: 5, 15: 6}
  military:  {0: 1, 5: 3, 10: 4, 14: 5}
missions:
  - id: investigate-the-burn
    name: "Investigate the Burn"
    vp: null
---

# Burnham: Basic side

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
| Military | ×1 |  |  |  |  | ×3 |  |  |  |  | ×4 |  |  |  | ×5 |  |

## Missions

### Investigate the Burn

- **Printed goal:** Have 2 Incident, a Scientist, and a Kelpien on the same Ship, and [Research] at 5+.
- **Goal check:** one deployed Ship whose card plus its beamed cards include 2 Incidents, a Scientist and a Kelpien (REQ-MS-03); and Research 5 or more.
- **Printed reward:** Take the top Discovery and put it on the top of your deck. Recrystallize up to 2 [Dilithium].
- **Reward steps:**
  1. Take the top Encounter onto the top of your Draw deck.
  2. Recrystallize up to 2 Dilithium.
- **Actions used:** `TAKE_ENCOUNTER`, `MOVE_RESOURCES`
- **Undoable:** no
- **VP:** none on the Basic side.

## Rulings and open questions

- Ruling (confirmed 2026-10-09): "Discovery" on the Core Box boards is the Encounter suit (the pill carries the Encounter icon).
- Recrystallize moves Dilithium from Inert Dilithium to your supply (KW-RECRY-01).
- The beamed cards that met the goal are dismissed afterwards (REQ-MS-06).

## Tests

- Given the goal of Investigate the Burn is met, when the mission is completed, then its reward resolves.
