---
id: cb-georgiou-advanced
captain: georgiou
side: advanced
scan: cb-georgiou-advanced.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 3
tracks:
  research:  {2: 1, 7: 2, 10: 3, 13: 4, 15: 5}
  influence: {3: 1, 8: 2, 11: 4, 15: 6}
  military:  {2: 1, 7: 2, 10: 3, 14: 4}
missions:
  - id: call-in-the-reinforcements
    name: Call in the Reinforcements
    vp: 3
  - id: hardly-a-negotiation
    name: Hardly a Negotiation
    vp: 3
  - id: gazing-at-the-stars
    name: Gazing at the Stars
    vp: 3
---

# Georgiou: Advanced side

## Turn summary

The same as the Basic side: Control max 1, Actions 3. The Advanced side has no room to print it.

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research | | | ×1 | | | | | ×2 | | | ×3 | | | ×4 | | ×5 |
| Influence | | | | ×1 | | | | | ×2 | | | ×4 | | | | ×6 |
| Military | | | ×1 | | | | | ×2 | | | ×3 | | | | ×4 | |

## Missions

### Call in the Reinforcements (3 VP)

Same goal and reward as the Basic side; see [cb-georgiou-basic.md](cb-georgiou-basic.md).

- **Actions used:** `SCAN`, `FREE_PLAY`, `GAIN_RESOURCE`, `DISMISS`
- **Undoable:** no

### Hardly a Negotiation (3 VP)

- **Printed goal:** Have 3 Person (excluding cards with Starfleet) on the same Ship, and have [Research], [Influence], and [Military] all at 1+.
- **Goal check:** one deployed Ship whose card plus its beamed cards include 3 or more Persons without Starfleet (REQ-MS-03); and all three tracks at 1 or more.
- **Printed reward:** You *may* enlist a Development. If you have 2+ Vulcan in play, either draw a card **OR** gain an [Action].
- **Reward steps:**
  1. You may enlist a Development, paying its cost.
  2. If you have 2 or more Vulcan cards in play, choose: draw a card, or gain an action.
- **Actions used:** `may`, `ENLIST_DEVELOPMENT`, `choose`, `DRAW`, `GAIN_ACTION`
- **Undoable:** no
- **Note:** the beamed Persons that met the goal are dismissed afterwards (REQ-MS-06).

### Gazing at the Stars (3 VP)

- **Printed goal:** Have [Research] at 7+, and 2 Alien in play.
- **Goal check:** Research track 7 or more, and 2 or more Alien cards in play.
- **Printed reward:** Enlist *Kaminar* for free. Draw a card for each Scientist you have in play.
- **Reward steps:**
  1. Enlist Kaminar (2GEO03) from the Development pile, ignoring its development cost (KW-ENDEV-04).
  2. Draw one card per Scientist card you have in play.
- **Actions used:** `ENLIST_DEVELOPMENT`, `DRAW`
- **Undoable:** no

## Rulings and open questions

- If Kaminar has already left the Development pile, the first reward step does nothing.

## Tests

- Given Military reached 14, then the Military multiplier is ×4; given it never reached 2, Military Focus cards score 0.
- Given 3 non-Starfleet Persons beamed to one Ship and all tracks at 1+, then Hardly a Negotiation can be completed.
- Given Kaminar in the Development pile, when Gazing at the Stars completes, then Kaminar goes on top of the Draw deck with no cost paid.
