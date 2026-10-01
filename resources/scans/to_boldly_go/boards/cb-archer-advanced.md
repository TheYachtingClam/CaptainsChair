---
id: cb-archer-advanced
captain: archer
side: advanced
scan: cb-archer-advanced.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 3
tracks:
  research: {3: 1, 8: 3, 15: 5}
  influence: {3: 1, 8: 3, 15: 6}
  military: {3: 1, 8: 3, 15: 5}
missions:
  - id: history-with-every-light-year
    name: History with Every Light-Year
    vp: 4
  - id: coalition-of-planets
    name: Coalition of Planets
    vp: 3
  - id: temporal-cold-war
    name: Temporal Cold War
    vp: 2
---

# Archer: Advanced side

## Turn summary

The same as the Basic side: Control max 1, Actions 3. The Advanced side has no room to print it.

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research |  |  |  | ×1 |  |  |  |  | ×3 |  |  |  |  |  |  | ×5 |
| Influence |  |  |  | ×1 |  |  |  |  | ×3 |  |  |  |  |  |  | ×6 |
| Military |  |  |  | ×1 |  |  |  |  | ×3 |  |  |  |  |  |  | ×5 |

Spaces before the first multiplier score ×0 for Focus icons.

## Missions

### History with Every Light-Year (4 VP)

- **Printed goal:** Have the *NX-01 Enterprise* and an [Away Team] at a secured neutral Location. Have 1 Person on the *NX-01 Enterprise* and at least 4 [Dilithium].
- **Goal check:** The NX-01 Enterprise (2ARC03) and one of your Away Teams are at the same neutral Location that you have secured; a Person is beamed to the NX-01 Enterprise; and you have 4 or more Dilithium.
- **Printed reward:** You *may* spend 4 [Dilithium] to take control of the *NX-01 Enterprise*'s Location. You *may* find either *Inspire* or *Strength of the Soul*.
- **Reward steps:**
  1. You may spend 4 Dilithium to take control of the NX-01 Enterprise's Location.
  2. You may find Inspire (2ARC15) or Strength of the Soul (2ARC22).
- **Actions used:** `SPEND`, `TAKE_CONTROL`, `FIND`
- **Undoable:** no

### Coalition of Planets (3 VP)

- **Printed goal:** Have an Andorian, a Vulcan, and a Tellarite at the same controlled Location, and a Communication in play.
- **Goal check:** One of your controlled Locations has, among its own card, Ships there and cards beamed there, an Andorian, a Vulcan and a Tellarite (REQ-MS-04); and you have a Communication in play.
- **Printed reward:** Scan 2 of Person **OR** scan 1 of Ally. Draw a card. You *may* destroy a Romulan from your Discard pile to gain 3 [Glory].
- **Reward steps:**
  1. Choose: scan 2 of Person, or scan 1 of Ally.
  2. Draw a card.
  3. You may destroy a Romulan from your Discard pile to gain 3 Glory.
- **Actions used:** `SCAN`, `DRAW`, `DESTROY`, `GAIN_RESOURCE`
- **Undoable:** no

### Temporal Cold War (2 VP)

- **Printed goal:** Have 5 Different Species (excluding Human), 2 Time Travel, and an Incident in play.
- **Goal check:** Your in-play cards show 5 or more different species traits other than Human; 2 or more Time Travel cards; and an Incident.
- **Printed reward:** Gain an [Action]. You *may* log a deployed Ship to gain an (additional) [Action].
- **Reward steps:**
  1. Gain an action.
  2. You may log one of your deployed Ships to gain another action.
- **Actions used:** `GAIN_ACTION`, `LOG`
- **Undoable:** yes

## Rulings and open questions

- Influence tops out at ×6 and Research and Military at ×5, as printed.

## Tests

- Given the goal is met, then the mission can be completed and its Mission Completion token placed (REQ-MS-06).
