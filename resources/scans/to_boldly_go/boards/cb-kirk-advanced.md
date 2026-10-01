---
id: cb-kirk-advanced
captain: kirk
side: advanced
scan: cb-kirk-advanced.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 3
tracks:
  research: {2: 1, 3: 2, 6: 3, 10: 4}
  influence: {2: 1, 3: 2, 6: 3, 10: 4}
  military: {2: 1, 3: 2, 6: 3, 10: 4}
missions:
  - id: where-no-man-has-gone-before
    name: Where No Man Has Gone Before
    vp: 4
  - id: the-undiscovered-country
    name: The Undiscovered Country
    vp: 1
  - id: search-for-spock
    name: Search for Spock
    vp: 4
---

# Kirk: Advanced side

## Turn summary

The same as the Basic side: Control max 1, Actions 3. The Advanced side has no room to print it.

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research |  |  | ×1 | ×2 |  |  | ×3 |  |  |  | ×4 |  |  |  |  |  |
| Influence |  |  | ×1 | ×2 |  |  | ×3 |  |  |  | ×4 |  |  |  |  |  |
| Military |  |  | ×1 | ×2 |  |  | ×3 |  |  |  | ×4 |  |  |  |  |  |

Spaces before the first multiplier score ×0 for Focus icons.

## Missions

### Where No Man Has Gone Before (4 VP)

- **Printed goal:** Have 2 Encounter on the same Ship, and [Research] at 4+.
- **Goal check:** One deployed Ship, counting the Ship and cards beamed to it, has 2 or more Encounters (REQ-MS-03); and your Research track is 4 or more.
- **Printed reward:** Take the top Encounter. Remove 2 [Glory] from the Stardate card.
- **Reward steps:**
  1. Take the top Encounter.
  2. Remove 2 Glory from the current Stardate card and return them to the supply.
- **Actions used:** `TAKE_ENCOUNTER`
- **Undoable:** no

### The Undiscovered Country (1 VP)

- **Printed goal:** Have 3 of the same Any Species (excluding cards with Human / Starfleet) in play, and [Influence] at 4+.
- **Goal check:** 3 or more of your in-play cards without Human or Starfleet share one species trait; and Influence is 4 or more.
- **Printed reward:** Enlist a Development for free.
- **Reward steps:**
  1. Enlist a Development, ignoring its development cost (KW-ENDEV-04).
- **Actions used:** `ENLIST_DEVELOPMENT`
- **Undoable:** yes

### Search for Spock (4 VP)

- **Printed goal:** Have *Captain Spock* logged, the *H.M.S. Bounty* in play, 5 Person in play, and [Military] at 4+.
- **Goal check:** Captain Spock (2KIRK24) is in your Log; H.M.S. Bounty (2KIRK11) is in play; 5 or more Persons are in play; and Military is 4 or more.
- **Printed reward:** Draw *Captain Spock* from your Log, and you *may* free play *Captain Spock*. You *may* find an Incident and return it. Gain an [Action]. Dismiss the *H.M.S. Bounty*.
- **Reward steps:**
  1. Take Captain Spock from your Log into hand.
  2. You may free play Captain Spock.
  3. You may find an Incident and return it.
  4. Gain an action.
  5. Dismiss the H.M.S. Bounty.
- **Actions used:** `FREE_PLAY`, `FIND`, `RETURN_INCIDENT`, `GAIN_ACTION`, `DISMISS`
- **Undoable:** no

## Rulings and open questions

- Taking Captain Spock from the Log needs a DRAW_FROM_LOG action, which CLAUDE.md does not have yet.
- Where No Man Has Gone Before needs the REMOVE_STARDATE_GLORY action noted on the Basic side.

## Tests

- Given the goal is met, then the mission can be completed and its Mission Completion token placed (REQ-MS-06).
