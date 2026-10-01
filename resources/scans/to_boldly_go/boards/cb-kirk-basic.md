---
id: cb-kirk-basic
captain: kirk
side: basic
scan: cb-kirk-basic.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 1
tracks:
  research: {0: 1, 2: 2, 3: 3, 6: 4, 10: 5}
  influence: {0: 1, 2: 2, 3: 3, 6: 4, 10: 5}
  military: {0: 1, 2: 2, 3: 3, 6: 4, 10: 5}
missions:
  - id: where-no-man-has-gone-before
    name: Where No Man Has Gone Before
    vp: null
---

# Kirk: Basic side

## Turn summary

1. Resupply
2. Control (max 1)
3. Actions (3)
4. Clean-up: A. Resolve Stardate, B. Place Glory, C. Discard & Draw

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research | ×1 |  | ×2 | ×3 |  |  | ×4 |  |  |  | ×5 |  |  |  |  |  |
| Influence | ×1 |  | ×2 | ×3 |  |  | ×4 |  |  |  | ×5 |  |  |  |  |  |
| Military | ×1 |  | ×2 | ×3 |  |  | ×4 |  |  |  | ×5 |  |  |  |  |  |

## Missions

### Where No Man Has Gone Before

- **Printed goal:** Have 2 Encounter on the same Ship, and [Research] at 4+.
- **Goal check:** One deployed Ship, counting the Ship and cards beamed to it, has 2 or more Encounters (REQ-MS-03); and your Research track is 4 or more.
- **Printed reward:** Take the top Encounter. Remove 2 [Glory] from the Stardate card.
- **Reward steps:**
  1. Take the top Encounter.
  2. Remove 2 Glory from the current Stardate card and return them to the supply.
- **Actions used:** `TAKE_ENCOUNTER`, `REMOVE_STARDATE_GLORY`
- **Undoable:** no
- **VP:** none on the Basic side.

## Rulings and open questions

- Removing Glory from the Stardate card brings the game end closer; if it empties the card, the normal emptying rules apply (REQ-SD-02).

## Tests

- Given the goal is met, then the mission can be completed and its Mission Completion token placed (REQ-MS-06).
