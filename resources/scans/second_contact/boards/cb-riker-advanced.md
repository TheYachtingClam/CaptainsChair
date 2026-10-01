---
id: cb-riker-advanced
captain: riker
side: advanced
scan: cb-riker-advanced.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 3
tracks:
  research: {8: 2, 11: 3, 13: 4}
  influence: {5: 2, 10: 3, 14: 4}
  military: {2: 1, 7: 2, 11: 3, 15: 5}
missions:
  - id: battling-the-pakled
    name: Battling the Pakled
    vp: 3
  - id: spirit-of-starfleet
    name: Spirit of Starfleet
    vp: 2
  - id: messages-from-old-friends
    name: Messages from Old Friends
    vp: 2
---

# Riker: Advanced side

## Turn summary

The same as the Basic side: Control max 1, Actions 3. The Advanced side has no room to print it.

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research |  |  |  |  |  |  |  |  | ×2 |  |  | ×3 |  | ×4 |  |  |
| Influence |  |  |  |  |  | ×2 |  |  |  |  | ×3 |  |  |  | ×4 |  |
| Military |  |  | ×1 |  |  |  |  | ×2 |  |  |  | ×3 |  |  |  | ×5 |

Spaces before the first multiplier score ×0 for Focus icons.

## Missions

### Battling the Pakled (3 VP)

- **Printed goal:** Meet 2 of the following 3 criteria: have a Pakled logged **OR** have [Military] at 8+ **OR** have [Influence] at 4+.
- **Goal check:** At least 2 of: a Pakled card in your Log; Military 8 or more; Influence 4 or more.
- **Printed reward:** Gain 3 [Dilithium]/[Latinum]. Up to twice, send an [Away Team] to a Location. If you meet all 3 criteria, gain 2 [Glory].
- **Reward steps:**
  1. Gain 3 resources, each Dilithium or Latinum as you choose.
  2. Up to twice, send an Away Team to a Location.
  3. If all 3 criteria are met, gain 2 Glory.
- **Actions used:** `GAIN_RESOURCE`, `SEND_AWAY_TEAM`
- **Undoable:** yes

### Spirit of Starfleet (2 VP)

- **Printed goal:** Have a Starfleet on duty, and have 5 cards with [Research]/[Any Skill] in play (excluding beamed cards).
- **Goal check:** A Starfleet Duty Officer; and 5 or more non-beamed in-play cards with a Research or Any Skill icon.
- **Printed reward:** Gain an [Action]. Scan for Any Species of your choice. (Name the species before scanning.)
- **Reward steps:**
  1. Gain an action.
  2. Name a species, then scan for it.
- **Actions used:** `GAIN_ACTION`, `SCAN_FOR`
- **Undoable:** no

### Messages from Old Friends (2 VP)

- **Printed goal:** Have 4 different of Klingon / Pilot / Doctor / Scientist / Synthetic in play.
- **Goal check:** Your in-play cards show at least 4 of these 5 traits: Klingon, Pilot, Doctor, Scientist, Synthetic.
- **Printed reward:** Refresh your Captain. Take the bottom Encounter.
- **Reward steps:**
  1. Refresh your Captain.
  2. Take the bottom card of the Encounter deck.
- **Actions used:** `REFRESH`, `TAKE_ENCOUNTER`
- **Undoable:** no

## Rulings and open questions

- Taking the bottom Encounter needs TAKE_ENCOUNTER to accept a bottom-of-deck option.

## Tests

- Given the goal is met, then the mission can be completed and its Mission Completion token placed (REQ-MS-06).
