---
id: cb-freeman-advanced
captain: freeman
side: advanced
scan: cb-freeman-advanced.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 3
tracks:
  research: {2: 1, 7: 2, 10: 3, 13: 4, 15: 5}
  influence: {2: 1, 7: 2, 10: 3, 13: 4, 15: 5}
  military: {2: 1, 7: 2, 10: 3, 13: 4, 15: 5}
missions:
  - id: project-swing-by
    name: Project Swing By
    vp: 4
  - id: beta-shift
    name: Beta Shift
    vp: 1
  - id: calling-all-your-friends
    name: Calling All Your Friends
    vp: 1
---

# Freeman: Advanced side

## Turn summary

The same as the Basic side: Control max 1, Actions 3. The Advanced side has no room to print it.

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research |  |  | ×1 |  |  |  |  | ×2 |  |  | ×3 |  |  | ×4 |  | ×5 |
| Influence |  |  | ×1 |  |  |  |  | ×2 |  |  | ×3 |  |  | ×4 |  | ×5 |
| Military |  |  | ×1 |  |  |  |  | ×2 |  |  | ×3 |  |  | ×4 |  | ×5 |

Spaces before the first multiplier score ×0 for Focus icons.

## Missions

### Project Swing By (4 VP)

- **Printed goal:** Have 4 Ally on the same Ship, and at least two of [Military]/[Influence]/[Research] at 4+.
- **Goal check:** One deployed Ship, with its beamed cards, has 4 or more Allies (REQ-MS-03); and at least 2 of your 3 tracks are at 4 or more.
- **Printed reward:** Gain 4 [Dilithium] and draw 4 cards. You *may* junk a card from the Market.
- **Reward steps:**
  1. Gain 4 Dilithium.
  2. Draw 4 cards.
  3. You may junk a Market card.
- **Actions used:** `GAIN_RESOURCE`, `DRAW`, `JUNK`
- **Undoable:** no

### Beta Shift (1 VP)

- **Printed goal:** Have 4 Person including at least 2 Lower Decker on the same Ship.
- **Goal check:** One deployed Ship, with its beamed cards, has 4 or more Persons, of which 2 or more are Lower Deckers.
- **Printed reward:** You *may* scan for an Anomaly. You *may* send an [Away Team] to a Location. Gain 2 [Glory].
- **Reward steps:**
  1. You may scan for an Anomaly.
  2. You may send an Away Team to a Location.
  3. Gain 2 Glory.
- **Actions used:** `SCAN_FOR`, `SEND_AWAY_TEAM`, `GAIN_RESOURCE`
- **Undoable:** no

### Calling All Your Friends (1 VP)

- **Printed goal:** Have 5 Ship (deployed and/or beamed) at the same neutral Location.
- **Goal check:** One neutral Location has 5 or more of your Ships there, counting deployed Ships at it and Ships beamed to them or to it. The California-class fleet's double weight applies only to securing, not here.
- **Printed reward:** Two times: Gain 1 [Research]/[Influence]/[Military], whichever is lowest. Scan for either [Research Focus] or [Influence Focus] or [Military Focus].
- **Reward steps:**
  1. Twice: gain 1 in your lowest Specialty; ties go Research, Influence, Military.
  2. Scan for a card with a Research, Influence or Military Focus icon.
- **Actions used:** `GAIN_SPECIALTY`, `SCAN_FOR`
- **Undoable:** no

## Rulings and open questions

- The scan icons in Calling All Your Friends have folded corners, so they are Focus icons.

## Tests

- Given the goal is met, then the mission can be completed and its Mission Completion token placed (REQ-MS-06).
