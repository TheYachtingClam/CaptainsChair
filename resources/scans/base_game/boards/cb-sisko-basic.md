---
id: cb-sisko-basic
captain: sisko
side: basic
scan: cb-sisko-basic.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 1
tracks:
  research:  {0: 1, 3: 2, 8: 3, 11: 5, 15: 7}
  influence: {0: 1, 2: 2, 7: 3, 10: 4, 13: 5, 15: 6}
  military:  {0: 1, 4: 2, 9: 4, 13: 5, 15: 6}
missions:
  - id: a-call-to-arms
    name: "A Call to Arms"
    vp: null
---

# Sisko: Basic side

## Turn summary

1. Resupply
2. Control (max 1)
3. Actions (3)
4. Clean-up: A. Resolve Stardate, B. Place Glory, C. Discard & Draw

## Specialty tracks

| Space | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Research | ×1 |  |  | ×2 |  |  |  |  | ×3 |  |  | ×5 |  |  |  | ×7 |
| Influence | ×1 |  | ×2 |  |  |  |  | ×3 |  |  | ×4 |  |  | ×5 |  | ×6 |
| Military | ×1 |  |  |  | ×2 |  |  |  |  | ×4 |  |  |  | ×5 |  | ×6 |

## Missions

### A Call to Arms

- **Printed goal:** Have 4 Ship deployed. Have [Influence] at 7+ **OR** [Military] at 7+.
- **Goal check:** 4 or more deployed Ships; and Influence 7 or more, or Military 7 or more.
- **Printed reward:** Enlist a Development, reducing the cost by 1 [Dilithium] or 1 [Latinum] for each Starbase you have in play.
- **Reward steps:**
  1. Enlist a Development. For each Starbase you have in play, its cost is 1 Dilithium or 1 Latinum less, your choice each time.
- **Actions used:** `ENLIST_DEVELOPMENT`
- **Undoable:** yes
- **VP:** none on the Basic side.

## Rulings and open questions

- Needs ENLIST_DEVELOPMENT to take a discount of several resources; today `discount=True` is one.
- Ruling (confirmed 2026-10-10): for *A Call to Arms*, for each Starbase in play you choose whether it takes off 1 Dilithium or 1 Latinum. *Deep Space 9* counts.

## Tests

- Given the goal of A Call to Arms is met, when the mission is completed, then its reward resolves.
