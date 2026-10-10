---
id: cb-shran-advanced
captain: shran
side: advanced
scan: cb-shran-advanced.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 3
tracks:
  research:  {5: 2, 10: 3, 14: 4}
  influence: {2: 1, 7: 2, 10: 3, 13: 4, 15: 5}
  military:  {3: 1, 8: 2, 11: 4, 15: 5}
missions:
  - id: securing-andorias-borders
    name: "Securing Andoria's Borders"
    vp: 2
  - id: founding-the-federation
    name: "Founding the Federation"
    vp: 4
  - id: andorian-mining-consortium
    name: "Andorian Mining Consortium"
    vp: 3
---

# Shran: Advanced side

## Turn summary

The same as the Basic side: Control max 1, Actions 3. The Advanced side has no room to print it.

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research |  |  |  |  |  | ×2 |  |  |  |  | ×3 |  |  |  | ×4 |  |
| Influence |  |  | ×1 |  |  |  |  | ×2 |  |  | ×3 |  |  | ×4 |  | ×5 |
| Military |  |  |  | ×1 |  |  |  |  | ×2 |  |  | ×4 |  |  |  | ×5 |

## Missions

### Securing Andoria's Borders (2 VP)

Same goal and reward as the Basic side; see [cb-shran-basic.md](cb-shran-basic.md).

- **Actions used:** `SCAN`, `DRAW`, `GAIN_ACTION`
- **Undoable:** no

### Founding the Federation (4 VP)

- **Printed goal:** Have 1 Human and 3 different of Vulcan / Tellarite / Andorian / Alien / Ambassador / Communication on the same Ship.
- **Goal check:** one deployed Ship whose card plus its beamed cards include a Human, and cards covering 3 different traits of the six listed (REQ-MS-03). One card counts for one trait.
- **Printed reward:** Gain 2 [Research], 2 [Influence], and 2 [Military]. You *may* send an [Away Team] to a Location with Starbase.
- **Reward steps:**
  1. Gain 2 Research, 2 Influence and 2 Military.
  2. You may send an Away Team to a Starbase Location.
- **Actions used:** `GAIN_SPECIALTY`, `SEND_AWAY_TEAM`
- **Undoable:** yes

### Andorian Mining Consortium (3 VP)

- **Printed goal:** Have 3 Business in play.
- **Goal check:** 3 or more Business cards in play.
- **Printed reward:** Scan 1 of Cargo, gain 2 [Latinum] and 1 [Glory]. You *may* free play an Incident to gain 1 [Glory].
- **Reward steps:**
  1. Scan 1 of Cargo.
  2. Gain 2 Latinum and 1 Glory.
  3. You may free play an Incident; if you do, gain 1 Glory.
- **Actions used:** `SCAN`, `GAIN_RESOURCE`, `FREE_PLAY`
- **Undoable:** no

## Rulings and open questions

- Ruling (confirmed 2026-10-09): the Human and the three other traits come from four different cards; the Human card cannot also supply one of the other traits.
- Ruling (confirmed 2026-10-10): for *Founding the Federation*, the Ship card itself counts as a card "on the same Ship", as the rulebook says (p. 20, REQ-MS-03), so the Andorian *Kumari* supplies Andorian.

## Tests

- Given the goal of Founding the Federation is met, when the mission is completed, then its reward resolves.
- Given the goal of Andorian Mining Consortium is met, when the mission is completed, then its reward resolves.
