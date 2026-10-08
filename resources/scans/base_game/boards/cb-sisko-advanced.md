---
id: cb-sisko-advanced
captain: sisko
side: advanced
scan: cb-sisko-advanced.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 3
tracks:
  research:  {3: 1, 8: 2, 11: 4, 15: 6}
  influence: {2: 1, 7: 2, 10: 3, 13: 4, 15: 5}
  military:  {4: 1, 9: 3, 13: 4, 15: 5}
missions:
  - id: a-call-to-arms
    name: "A Call to Arms"
    vp: 4
  - id: bajors-application-to-the-federation
    name: "Bajor's Application to the Federation"
    vp: 5
  - id: contacting-the-dominion
    name: "Contacting the Dominion"
    vp: 3
---

# Sisko: Advanced side

## Turn summary

The same as the Basic side: Control max 1, Actions 3. The Advanced side has no room to print it.

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research |  |  |  | ×1 |  |  |  |  | ×2 |  |  | ×4 |  |  |  | ×6 |
| Influence |  |  | ×1 |  |  |  |  | ×2 |  |  | ×3 |  |  | ×4 |  | ×5 |
| Military |  |  |  |  | ×1 |  |  |  |  | ×3 |  |  |  | ×4 |  | ×5 |

## Missions

### A Call to Arms (4 VP)

Same goal and reward as the Basic side; see [cb-sisko-basic.md](cb-sisko-basic.md).

- **Actions used:** `ENLIST_DEVELOPMENT`
- **Undoable:** yes

### Bajor's Application to the Federation (5 VP)

- **Printed goal:** Have 2 Starfleet (excluding your Captain) and 3 Bajoran in play. Have a Ship at *Bajor*.
- **Goal check:** 2 or more Starfleet cards in play besides your Captain; 3 or more Bajoran cards in play; and one of your Ships at Bajor (1SIS02).
- **Printed reward:** Trigger the control operation of one of your controlled Location. Refresh *Bajor*.
- **Reward steps:**
  1. Resolve the CONTROL of one Location you control.
  2. Refresh Bajor.
- **Actions used:** `TRIGGER_CONTROL`, `REFRESH`
- **Undoable:** yes

### Contacting the Dominion (3 VP)

- **Printed goal:** have 3 Dominion / Changeling in play.
- **Goal check:** 3 or more cards in play that are Dominion or Changeling.
- **Printed reward:** Gain 3 [Influence]. Scan 1 of either Person, Cargo, or Ship. Draw 2 cards.
- **Reward steps:**
  1. Gain 3 Influence.
  2. Scan 1 of Person, Cargo or Ship.
  3. Draw 2 cards.
- **Actions used:** `GAIN_SPECIALTY`, `SCAN`, `DRAW`
- **Undoable:** no

## Rulings and open questions

None.

## Tests

- Given the goal of Bajor's Application to the Federation is met, when the mission is completed, then its reward resolves.
- Given the goal of Contacting the Dominion is met, when the mission is completed, then its reward resolves.
