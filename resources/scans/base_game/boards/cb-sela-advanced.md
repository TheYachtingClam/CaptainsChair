---
id: cb-sela-advanced
captain: sela
side: advanced
scan: cb-sela-advanced.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 3
tracks:
  research:  {5: 2, 10: 3, 14: 4}
  influence: {5: 2, 10: 3, 14: 4}
  military:  {5: 2, 10: 3, 14: 4}
missions:
  - id: romulan-might
    name: "Romulan Might"
    vp: 4
  - id: the-reunification-plot
    name: "The Reunification Plot"
    vp: 4
  - id: the-duras-plot
    name: "The Duras Plot"
    vp: 1
---

# Sela: Advanced side

## Turn summary

The same as the Basic side: Control max 1, Actions 3. The Advanced side has no room to print it.

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research |  |  |  |  |  | ×2 |  |  |  |  | ×3 |  |  |  | ×4 |  |
| Influence |  |  |  |  |  | ×2 |  |  |  |  | ×3 |  |  |  | ×4 |  |
| Military |  |  |  |  |  | ×2 |  |  |  |  | ×3 |  |  |  | ×4 |  |

## Missions

### Romulan Might (4 VP)

Same goal and reward as the Basic side; see [cb-sela-basic.md](cb-sela-basic.md).

- **Actions used:** `ENLIST_DEVELOPMENT`, `FIND`
- **Undoable:** no

### The Reunification Plot (4 VP)

- **Printed goal:** Have 4 Vulcan in play.
- **Goal check:** 4 or more Vulcan cards in play.
- **Printed reward:** Gain 3 [Influence]. Draw a card for each Shady you have in play. You *may* free play an Incident. You *may* junk a card from the Market.
- **Reward steps:**
  1. Gain 3 Influence.
  2. Draw a card for each Shady you have in play.
  3. You may free play an Incident.
  4. You may junk a card from the Market.
- **Actions used:** `GAIN_SPECIALTY`, `DRAW`, `FREE_PLAY`, `JUNK`
- **Undoable:** no

### The Duras Plot (1 VP)

- **Printed goal:** Have 1+ Klingon on the same Ship that has Cloak.
- **Goal check:** a deployed Cloak Ship with at least one Klingon card beamed to it.
- **Printed reward:** Gain 1 [Military] for each Cloak in play. Gain 2 [Glory] from the supply (not the Stardate card) for each Klingon in play. Dismiss one Cloak and all beamed Klingon.
- **Reward steps:**
  1. Gain 1 Military for each Cloak you have in play.
  2. Gain 2 Glory from the supply for each Klingon you have in play.
  3. Dismiss one of your Cloak cards and every beamed Klingon you have.
- **Actions used:** `GAIN_SPECIALTY`, `GAIN_RESOURCE`, `DISMISS`
- **Undoable:** yes

## Rulings and open questions

- Ruling (confirmed 2026-10-10): for *The Duras Plot*, you choose which one Cloak to dismiss; a Cloak in your Staging Area cannot be chosen.

## Tests

- Given the goal of The Reunification Plot is met, when the mission is completed, then its reward resolves.
- Given the goal of The Duras Plot is met, when the mission is completed, then its reward resolves.
