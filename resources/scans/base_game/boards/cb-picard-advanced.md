---
id: cb-picard-advanced
captain: picard
side: advanced
scan: cb-picard-advanced.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 3
tracks:
  research:  {2: 1, 7: 2, 10: 3, 13: 4, 15: 5}
  influence: {3: 1, 8: 2, 11: 4, 15: 6}
  military:  {5: 2, 10: 3, 14: 4}
missions:
  - id: peace-negotiations
    name: "Peace Negotiations"
    vp: 5
  - id: arbiter-of-succession
    name: "Arbiter of Succession"
    vp: 3
  - id: seek-out-new-life
    name: "Seek Out New Life"
    vp: 2
---

# Picard: Advanced side

## Turn summary

The same as the Basic side: Control max 1, Actions 3. The Advanced side has no room to print it.

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research |  |  | ×1 |  |  |  |  | ×2 |  |  | ×3 |  |  | ×4 |  | ×5 |
| Influence |  |  |  | ×1 |  |  |  |  | ×2 |  |  | ×4 |  |  |  | ×6 |
| Military |  |  |  |  |  | ×2 |  |  |  |  | ×3 |  |  |  | ×4 |  |

## Missions

### Peace Negotiations (5 VP)

Same goal and reward as the Basic side; see [cb-picard-basic.md](cb-picard-basic.md).

- **Actions used:** `GAIN_RESOURCE`, `DRAW`, `JUNK`
- **Undoable:** no

### Arbiter of Succession (3 VP)

- **Printed goal:** Have 3 Klingon on the same Ship.
- **Goal check:** one deployed Ship whose card plus its beamed cards include 3 or more Klingon cards (REQ-MS-03).
- **Printed reward:** Gain 1 [Glory], and 1 [Influence]/[Military]. Gain an [Action]. You *may* junk a card from the Market.
- **Reward steps:**
  1. Gain 1 Glory.
  2. Gain 1 Influence or 1 Military, your choice.
  3. Gain an action.
  4. You may junk a card from the Market.
- **Actions used:** `GAIN_RESOURCE`, `GAIN_SPECIALTY`, `GAIN_ACTION`, `JUNK`
- **Undoable:** no

### Seek Out New Life (2 VP)

- **Printed goal:** have 6 Different Species (excluding cards with Human/Starfleet) in play. Each Alien and each Transcendent counts as a different one.
- **Goal check:** among your cards in play without Human or Starfleet: the number of different Species traits, counting every Alien card and every Transcendent card as its own, is 6 or more.
- **Printed reward:** Take the top Discovery.
- **Reward steps:**
  1. Take the top Encounter.
- **Actions used:** `TAKE_ENCOUNTER`
- **Undoable:** no

## Rulings and open questions

- Ruling (confirmed 2026-10-09): "Discovery" on the Core Box boards is the Encounter suit (the pill carries the Encounter icon).
- Ruling (confirmed 2026-10-10): for *Seek Out New Life*, each Alien card and each Transcendent card is one species of its own, and its other Species traits are not counted as well. A Wildcard card is not counted.

## Tests

- Given the goal of Arbiter of Succession is met, when the mission is completed, then its reward resolves.
- Given the goal of Seek Out New Life is met, when the mission is completed, then its reward resolves.
