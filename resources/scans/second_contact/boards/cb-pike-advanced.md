---
id: cb-pike-advanced
captain: pike
side: advanced
scan: cb-pike-advanced.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 3
tracks:
  research: {9: 3, 14: 4}
  influence: {5: 2, 10: 3, 15: 5}
  military: {3: 1, 5: 2, 9: 3}
missions:
  - id: weight-of-the-future
    name: Weight of the Future
    vp: 3
  - id: boy-scout
    name: Boy Scout
    vp: 4
  - id: to-explore
    name: To Explore
    vp: 2
---

# Pike: Advanced side

## Turn summary

The same as the Basic side: Control max 1, Actions 3. The Advanced side has no room to print it.

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research |  |  |  |  |  |  |  |  |  | ×3 |  |  |  |  | ×4 |  |
| Influence |  |  |  |  |  | ×2 |  |  |  |  | ×3 |  |  |  |  | ×5 |
| Military |  |  |  | ×1 |  | ×2 |  |  |  | ×3 |  |  |  |  |  |  |

Spaces before the first multiplier score ×0 for Focus icons.

## Missions

### Weight of the Future (3 VP)

- **Printed goal:** Have 4 Time Travel in play (excluding your Captain) and 2 deployed Ongoing.
- **Goal check:** 4 or more Time Travel cards in play, not counting Christopher Pike; and 2 or more deployed Ongoing cards.
- **Printed reward:** Up to twice, return an Incident from your hand, Discard pile, or Log. For each Incident returned this way, draw a card.
- **Reward steps:**
  1. Up to twice: return an Incident from your hand, Discard pile or Log, then draw a card.
- **Actions used:** `RETURN_INCIDENT`, `DRAW`
- **Undoable:** no

### Boy Scout (4 VP)

- **Printed goal:** Have 7 Person in play, and [Influence] at 7+.
- **Goal check:** 7 or more Persons in play, and Influence 7 or more.
- **Printed reward:** Scan 2 of Ally. Refresh a card for each non-Starfleet Person you have in play.
- **Reward steps:**
  1. Scan 2 of Ally.
  2. Refresh one of your cards per non-Starfleet Person in play.
- **Actions used:** `SCAN`, `REFRESH`
- **Undoable:** no

### To Explore (2 VP)

- **Printed goal:** Have 2 Encounter in play, and have 3 Starfleet and an Alien/Anomaly at the same neutral Location.
- **Goal check:** 2 or more Encounters in play; and one neutral Location holds, among Ships there and beamed cards, 3 Starfleet cards and an Alien or Anomaly card (REQ-MS-04).
- **Printed reward:** Take control of the Location used to fulfill the goal. Remove 1 [Glory] from the Stardate card.
- **Reward steps:**
  1. Take control of that neutral Location.
  2. Remove 1 Glory from the current Stardate card.
- **Actions used:** `TAKE_CONTROL`
- **Undoable:** no

## Rulings and open questions

- Research on the Advanced side has only ×3 and ×4, so a low Research track scores 0.
- Removing Stardate Glory needs a REMOVE_STARDATE_GLORY action.

## Tests

- Given the goal is met, then the mission can be completed and its Mission Completion token placed (REQ-MS-06).
