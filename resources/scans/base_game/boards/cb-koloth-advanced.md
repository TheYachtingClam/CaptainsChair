---
id: cb-koloth-advanced
captain: koloth
side: advanced
scan: cb-koloth-advanced.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 3
tracks:
  research:  {5: 2, 10: 3, 14: 4}
  influence: {3: 1, 8: 2, 11: 4, 15: 6}
  military:  {2: 1, 7: 2, 10: 3, 13: 4, 15: 6}
missions:
  - id: expanding-the-empire
    name: "Expanding the Empire"
    vp: 3
  - id: romulan-weapons-trade-agreement
    name: "Romulan Weapons Trade Agreement"
    vp: 1
  - id: sabotage
    name: "Sabotage"
    vp: 4
---

# Koloth: Advanced side

## Turn summary

The same as the Basic side: Control max 1, Actions 3. The Advanced side has no room to print it.

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research |  |  |  |  |  | ×2 |  |  |  |  | ×3 |  |  |  | ×4 |  |
| Influence |  |  |  | ×1 |  |  |  |  | ×2 |  |  | ×4 |  |  |  | ×6 |
| Military |  |  | ×1 |  |  |  |  | ×2 |  |  | ×3 |  |  | ×4 |  | ×6 |

## Missions

### Expanding the Empire (3 VP)

Same goal and reward as the Basic side; see [cb-koloth-basic.md](cb-koloth-basic.md).

- **Actions used:** `ENLIST_RESERVE`, `ENLIST_DEVELOPMENT`, `DISMISS`
- **Undoable:** yes

### Romulan Weapons Trade Agreement (1 VP)

- **Printed goal:** Have 1 or more Romulan on a Ship that has Klingon.
- **Goal check:** a deployed Klingon Ship with at least one Romulan card beamed to it.
- **Printed reward:** Gain 1 [Military] for each Romulan in play. Enlist *Prototype Cloak* for free. You *may* junk a card from the Market.
- **Reward steps:**
  1. Gain 1 Military for each Romulan you have in play.
  2. Enlist Prototype Cloak (1KOL03) at no cost, if it is in your Development pile.
  3. You may junk a card from the Market.
- **Actions used:** `GAIN_SPECIALTY`, `ENLIST_DEVELOPMENT`, `JUNK`
- **Undoable:** no

### Sabotage (4 VP)

- **Printed goal:** have 2 Different Species (excluding cards with Klingon), 2 Weapon (excluding your Captain), and 1 Scientist in play.
- **Goal check:** among your non-Klingon cards in play, 2 or more different Species traits; 2 or more Weapon cards other than your Captain; and a Scientist.
- **Printed reward:** Enlist a Reserve. You *may* force your opponent to take 2 Incident.
- **Reward steps:**
  1. Enlist a Reserve.
  2. You may make the opponent take 2 Incidents (attack part).
- **Actions used:** `ENLIST_RESERVE`, `ATTACK`, `TAKE_INCIDENT`
- **Undoable:** no

## Rulings and open questions

- The beamed Romulans that met the goal are dismissed afterwards (REQ-MS-06); the Military is counted first.
- Printed as ATTACK REWARD: the opponent may ignore the Incidents with a 'when you would be attacked' Reaction.
- Ruling (confirmed 2026-10-10): for *Sabotage*, you choose whether to attack; if you do, the opponent may ignore it.

## Tests

- Given the goal of Romulan Weapons Trade Agreement is met, when the mission is completed, then its reward resolves.
- Given the goal of Sabotage is met, when the mission is completed, then its reward resolves.
