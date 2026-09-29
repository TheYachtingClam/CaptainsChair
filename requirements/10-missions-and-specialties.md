# 10 – Specialties, Skill/Focus Icons and Missions

Source: Rulebook pp. 17, 20, 27.

## 1. Specialty tracks

- **REQ-SP-01** There are three Specialties, each a track on the Crew board: **Research** (blue), **Influence** (yellow), **Military** (red).
- **REQ-SP-02** Gaining a Specialty moves that marker one space right. Tracks run from 0 to 15 and cannot go higher.
- **REQ-SP-03** Some track spaces show a **VP multiplier** (e.g. space 10 = ×4). The multiplier positions differ per Crew board and per board side. They must be stored as board data.
- **REQ-SP-04** The engine must record the highest multiplier reached on each track. Scoring uses the highest multiplier reached, not the current step.

## 2. Skill and Focus icons

- **REQ-SP-10 Skill icons** sit in the upper-left corner below the title bar.
  - A card may show up to three.
  - Types: Research, Influence, Military, **Any** (counts as any one Specialty) and **Variable** ("?", changes under conditions the card states).
  - They are most often counted by *Utilize* to advance tracks.
- **REQ-SP-11 Focus icons** sit bottom-right next to the VP icon.
  - Types: Research, Influence, Military and **Best**.
  - They set the card's endgame value from the matching track's highest multiplier. Best uses the highest multiplier on any track.
  - They score only if the player completed at least one mission.
- **REQ-SP-12 Using specialties.** An effect requiring a card "exhibiting" a Specialty, e.g. discard a card with Military, is met by a matching Skill or Focus icon, or by Any Skill or Best Focus.
  - A card with only a matching **restriction** icon does not qualify.

## 3. Specialty restrictions

- **REQ-SP-20** Some operations show a **restriction**, e.g. "Requires Military 5". The operation can only be played or resolved if that track is at or above the value.
- **REQ-SP-21** The UI must show unavailable operations as disabled and explain why.

## 4. Missions

- **REQ-MS-01** Each Crew board side has one or more missions. Each has a **GOAL** and a **REWARD**.
- **REQ-MS-02** Goals usually require a Specialty track value, or certain suits or traits in play.
- **REQ-MS-03 "On the same Ship"** counts icons on one deployed Ship plus every card beamed to that Ship.
- **REQ-MS-04 "At the same Location"** counts icons on:
  - one Location,
  - every Ship at that Location,
  - every card beamed to those Ships or to the Location.
- **REQ-MS-05** While a goal is met, the player **may** complete the mission at any time in their Action Step. This does not cost an action.
- **REQ-MS-06 Completion procedure:**
  1. Determine which cards contributed.
  2. Resolve the REWARD.
  3. Dismiss all **beamed** contributing cards. Other in-play contributors are not dismissed: deployed Ships, Locations, Staging Area cards, etc.
     - A contributing beamed card that stops being beamed during the Reward (dismissed, promoted, logged) is not dismissed.
     - A contributing card that **becomes** beamed during the Reward is dismissed.
  4. Place a Mission Completion token on the mission.
- **REQ-MS-07** Each mission can be completed only once.
- **REQ-MS-08 Mission failed.** If no mission is completed, all Focus icons score 0 VP.
- **REQ-MS-09** The engine should evaluate goals continuously and show the player when a mission is completable. It must never auto-complete, because completing is optional and its timing matters.
- **REQ-MS-10** Wording such as "Have Cmdr. Burnham on duty" requires the card in a Duty Officer slot. "In play" alone is not enough.
- **REQ-MS-11** Advanced-side missions have printed VP that score at game end (see [13-final-scoring.md](13-final-scoring.md)). The Basic side uses 1 Mission Completion token; the Advanced side uses 3.

## 5. Crew board data

Each Crew board side needs:

- Captain name and side label (Basic or Advanced).
- Mission list with goals, rewards and VP values on the Advanced side.
- Turn summary: Resupply, Control (max N), Actions (N), Clean-up with substeps.
- The three tracks with multiplier positions.
