---
id: cb-soval-basic
captain: soval
side: basic
scan: cb-soval-basic.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 1        # Basic side keeps 1 token (REQ-PS-01)
tracks:                              # track space -> multiplier, as printed; spaces not listed add nothing
  research:  {0: 1, 2: 2, 7: 3, 10: 4, 13: 5, 15: 6}
  influence: {0: 1, 3: 2, 8: 4, 11: 5, 15: 6}
  military:  {0: 1, 2: 2, 7: 3, 10: 4, 13: 5, 15: 6}
missions:
  - id: my-mind-to-your-mind
    name: My Mind to Your Mind
    vp: null                         # Basic side missions score no VP
---

# Soval: Basic side

## Turn summary

1. Resupply
2. Control (max 1)
3. Actions (3)
4. Clean-up: A. Resolve Stardate, B. Place Glory, C. Discard & Draw

## Specialty tracks

Each track runs 0 to 15. The multiplier used at scoring is the highest one the marker has reached (REQ-SP-04).

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research | ×1 | | ×2 | | | | | ×3 | | | ×4 | | | ×5 | | ×6 |
| Influence | ×1 | | | ×2 | | | | | ×4 | | | ×5 | | | | ×6 |
| Military | ×1 | | ×2 | | | | | ×3 | | | ×4 | | | ×5 | | ×6 |

Influence skips ×3 as printed.

## Missions

### My Mind to Your Mind

- **Printed goal:** Have 5 cards with [Research]/[Any Skill] in play (excluding beamed cards).
- **Goal check:** at least 5 of your in-play cards, not counting beamed cards, have a Research Skill icon or an Any Skill icon.
- **Printed reward:** For each Telepath you have in play, either: draw a card **OR** gain 1 [Latinum] and you *may* return an Incident.
- **Reward steps:**
  1. Count your in-play Telepath cards, including beamed ones.
  2. For each, choose: draw a card; or gain 1 Latinum and you may return an Incident.
- **Actions used:** `choose`, `DRAW`, `GAIN_RESOURCE`, `may`, `RETURN_INCIDENT`
- **Undoable:** no
- **VP:** none on the Basic side.

## Rulings and open questions

- The goal icons are Skill icons: Research and Any Skill. A card counts once even if it has several matching icons.

## Tests

- Given 5 non-beamed cards with a Research or Any Skill icon in play, then the mission can be completed.
- Given 4 such cards and 1 more that is beamed, then the mission cannot be completed.
- Given 2 Telepaths in play, when the reward resolves, the player makes 2 choices.
