---
id: cb-soval-advanced
captain: soval
side: advanced
scan: cb-soval-advanced.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 3
tracks:
  research:  {2: 1, 7: 2, 10: 3, 13: 4, 15: 5}
  influence: {3: 1, 8: 3, 11: 4, 15: 5}
  military:  {2: 1, 7: 2, 10: 3, 13: 4, 15: 5}
missions:
  - id: my-mind-to-your-mind
    name: My Mind to Your Mind
    vp: 2
  - id: cooperation-with-starfleet
    name: Cooperation with Starfleet
    vp: 4
  - id: the-needs-of-the-many
    name: The Needs of the Many
    vp: 3
---

# Soval: Advanced side

## Turn summary

The same as the Basic side: Control max 1, Actions 3. The Advanced side has no room to print it.

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research | | | ×1 | | | | | ×2 | | | ×3 | | | ×4 | | ×5 |
| Influence | | | | ×1 | | | | | ×3 | | | ×4 | | | | ×5 |
| Military | | | ×1 | | | | | ×2 | | | ×3 | | | ×4 | | ×5 |

Spaces 0 and 1 have no multiplier, so a track that never reaches its first multiplier scores ×0 for Focus icons. Influence skips ×2. Both are confirmed as printed.

## Missions

### My Mind to Your Mind (2 VP)

Same goal and reward as the Basic side; see [cb-soval-basic.md](cb-soval-basic.md).

- **Actions used:** `choose`, `DRAW`, `GAIN_RESOURCE`, `may`, `RETURN_INCIDENT`
- **Undoable:** no

### Cooperation with Starfleet (4 VP)

- **Printed goal:** Have 3 Ship deployed, 3 Starfleet beamed, and 1 Encounter in play.
- **Goal check:** all of: 3 or more deployed Ships; 3 or more of your beamed cards with Starfleet; 1 or more Encounters in play.
- **Printed reward:** Scan for either Human or Starfleet. You *may* send 1 [Away Team] each to up to 3 different Location.
- **Reward steps:**
  1. Choose Human or Starfleet and scan for it.
  2. You may send one Away Team to each of up to 3 different Locations.
- **Actions used:** `choose`, `SCAN_FOR`, `may`, `SEND_AWAY_TEAM`
- **Undoable:** no
- **Note:** the 3 beamed Starfleet cards helped complete the mission, so they are dismissed afterwards (REQ-MS-06).

### The Needs of the Many (3 VP)

- **Printed goal:** Have 5 Person and 2 Ally in play. Have [Influence] at 5+.
- **Goal check:** 5 or more Persons and 2 or more Allies in play, and the Influence track at 5 or more.
- **Printed reward:** Gain an [Action]. You *may* recall up to 2 beamed cards. You *may* log a Duty Officer to enlist a Development.
- **Reward steps:**
  1. Gain an action.
  2. You may recall up to 2 of your beamed cards.
  3. You may log a Duty Officer to enlist a Development, paying its cost.
- **Actions used:** `GAIN_ACTION`, `may`, `RECALL`, `LOG`, `ENLIST_DEVELOPMENT`
- **Undoable:** yes

## Rulings and open questions

- In The Needs of the Many, beamed Persons and Allies count toward the goal and are dismissed on completion, unless recalled by the reward first (REQ-MS-06).

## Tests

- Given Research at 1 at game end, then Research Focus cards score 0.
- Given Influence reached 9, then the Influence multiplier is ×3.
- Given 3 deployed Ships, 3 beamed Starfleet cards and an Encounter in play, then Cooperation with Starfleet can be completed and the beamed cards are dismissed.
