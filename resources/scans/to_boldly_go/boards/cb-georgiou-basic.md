---
id: cb-georgiou-basic
captain: georgiou
side: basic
scan: cb-georgiou-basic.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 1
tracks:
  research:  {0: 1, 2: 2, 7: 3, 10: 4, 13: 5, 15: 6}
  influence: {0: 1, 3: 2, 8: 3, 11: 5, 15: 7}
  military:  {0: 1, 2: 2, 7: 3, 10: 4, 14: 5}
missions:
  - id: call-in-the-reinforcements
    name: Call in the Reinforcements
    vp: null
---

# Georgiou: Basic side

## Turn summary

1. Resupply
2. Control (max 1)
3. Actions (3)
4. Clean-up: A. Resolve Stardate, B. Place Glory, C. Discard & Draw

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research | ×1 | | ×2 | | | | | ×3 | | | ×4 | | | ×5 | | ×6 |
| Influence | ×1 | | | ×2 | | | | | ×3 | | | ×5 | | | | ×7 |
| Military | ×1 | | ×2 | | | | | ×3 | | | ×4 | | | | ×5 | |

Influence jumps from ×3 to ×5 and ×7, and Military tops out at ×5 on space 14, as printed.

## Missions

### Call in the Reinforcements

- **Printed goal:** Have [Military] at 6+. Have *Cmdr. Burnham* on duty, and an Incident beamed to the *U.S.S. Shenzhou*.
- **Goal check:** all of: Military track 6 or more; Cmdr. Burnham (2GEO13) is a Duty Officer; at least one Incident is beamed to U.S.S. Shenzhou (2GEO02).
- **Printed reward:** Scan 1 of Ship and free play the gained card. Gain 3 [Dilithium]. If you have 1+ Klingon in play (excluding beamed cards), dismiss *Cmdr. Burnham* and gain 2 [Glory].
- **Reward steps:**
  1. Scan 1 of Ship.
  2. Free play the gained Ship.
  3. Gain 3 Dilithium.
  4. If you have a non-beamed Klingon in play, dismiss Cmdr. Burnham and gain 2 Glory.
- **Actions used:** `SCAN`, `FREE_PLAY`, `GAIN_RESOURCE`, `DISMISS`
- **Undoable:** no
- **VP:** none on the Basic side.

## Rulings and open questions

- The free-played Ship is played from wherever it was gained to (top of deck or Discard pile), since the reward names that card.
- Rulebook example (p. 20): the beamed Incident Hostile Contact is dismissed on completion; Burnham and the Shenzhou stay unless the Klingon clause applies.

## Tests

- Rulebook example p. 20 (AS-15): the reward resolves, the Klingon clause fails because Ash Tyler is beamed, and Hostile Contact is dismissed.
- Given Military 5, then the mission cannot be completed.
