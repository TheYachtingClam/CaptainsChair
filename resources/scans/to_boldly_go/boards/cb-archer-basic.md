---
id: cb-archer-basic
captain: archer
side: basic
scan: cb-archer-basic.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 1
tracks:
  research: {0: 1, 3: 2, 8: 4, 15: 6}
  influence: {0: 1, 3: 2, 8: 4, 15: 7}
  military: {0: 1, 3: 2, 8: 4, 15: 6}
missions:
  - id: history-with-every-light-year
    name: History with Every Light-Year
    vp: null
---

# Archer: Basic side

## Turn summary

1. Resupply
2. Control (max 1)
3. Actions (3)
4. Clean-up: A. Resolve Stardate, B. Place Glory, C. Discard & Draw

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research | ×1 |  |  | ×2 |  |  |  |  | ×4 |  |  |  |  |  |  | ×6 |
| Influence | ×1 |  |  | ×2 |  |  |  |  | ×4 |  |  |  |  |  |  | ×7 |
| Military | ×1 |  |  | ×2 |  |  |  |  | ×4 |  |  |  |  |  |  | ×6 |

## Missions

### History with Every Light-Year

- **Printed goal:** Have the *NX-01 Enterprise* and an [Away Team] at a secured neutral Location. Have 1 Person on the *NX-01 Enterprise* and at least 4 [Dilithium].
- **Goal check:** The NX-01 Enterprise (2ARC03) and one of your Away Teams are at the same neutral Location that you have secured; a Person is beamed to the NX-01 Enterprise; and you have 4 or more Dilithium.
- **Printed reward:** You *may* spend 4 [Dilithium] to take control of the *NX-01 Enterprise*'s Location. You *may* find either *Inspire* or *Strength of the Soul*.
- **Reward steps:**
  1. You may spend 4 Dilithium to take control of the NX-01 Enterprise's Location.
  2. You may find Inspire (2ARC15) or Strength of the Soul (2ARC22).
- **Actions used:** `SPEND`, `TAKE_CONTROL`, `FIND`
- **Undoable:** no
- **VP:** none on the Basic side.

## Rulings and open questions

- The beamed Person that met the goal is dismissed on completion (REQ-MS-06), unless the reward's take-control dismisses the Ship first.

## Tests

- Given the goal is met, then the mission can be completed and its Mission Completion token placed (REQ-MS-06).
