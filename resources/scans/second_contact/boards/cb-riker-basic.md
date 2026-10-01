---
id: cb-riker-basic
captain: riker
side: basic
scan: cb-riker-basic.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 1
tracks:
  research: {0: 1, 8: 3, 11: 4, 13: 5}
  influence: {0: 1, 5: 3, 10: 4, 14: 5}
  military: {0: 1, 2: 2, 7: 3, 11: 4, 15: 6}
missions:
  - id: battling-the-pakled
    name: Battling the Pakled
    vp: null
---

# Riker: Basic side

## Turn summary

1. Resupply
2. Control (max 1)
3. Actions (3)
4. Clean-up: A. Resolve Stardate, B. Place Glory, C. Discard & Draw

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research | ×1 |  |  |  |  |  |  |  | ×3 |  |  | ×4 |  | ×5 |  |  |
| Influence | ×1 |  |  |  |  | ×3 |  |  |  |  | ×4 |  |  |  | ×5 |  |
| Military | ×1 |  | ×2 |  |  |  |  | ×3 |  |  |  | ×4 |  |  |  | ×6 |

## Missions

### Battling the Pakled

- **Printed goal:** Meet 2 of the following 3 criteria: have a Pakled logged **OR** have [Military] at 8+ **OR** have [Influence] at 4+.
- **Goal check:** At least 2 of: a Pakled card in your Log; Military 8 or more; Influence 4 or more.
- **Printed reward:** Gain 3 [Dilithium]/[Latinum]. Up to twice, send an [Away Team] to a Location. If you meet all 3 criteria, gain 2 [Glory].
- **Reward steps:**
  1. Gain 3 resources, each Dilithium or Latinum as you choose.
  2. Up to twice, send an Away Team to a Location.
  3. If all 3 criteria are met, gain 2 Glory.
- **Actions used:** `GAIN_RESOURCE`, `SEND_AWAY_TEAM`
- **Undoable:** yes
- **VP:** none on the Basic side.

## Rulings and open questions

None.

## Tests

- Given the goal is met, then the mission can be completed and its Mission Completion token placed (REQ-MS-06).
