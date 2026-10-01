---
id: cb-khan
captain: khan
side: advanced
scan: cb-khan.jpg
turn_summary:
  control_max: 1
  actions: 3
mission_completion_tokens: 3
tracks: null                         # Khan has no Specialty tracks (REQ-CD-KHN-04)
missions:
  - id: ive-hurt-you
    name: I've Hurt You
    vp: 1
  - id: i-shall-leave-you-as-you-left-me
    name: I Shall Leave You as You Left Me
    vp: 2
  - id: marooned-for-all-eternity
    name: Marooned for All Eternity! Buried Alive!
    vp: 3
trait_slots: 12                       # trait names are printed under the tokens; not visible on this scan
---

# Khan: Advanced side

Khan has a single board, printed Advanced, with no Basic side. It uses 3 Mission Completion tokens.

## Turn summary

The same as the Basic side: Control max 1, Actions 3. The Advanced side has no room to print it.

## Specialty tracks

None. Khan's board has 12 trait slots instead (REQ-CD-KHN-06).

## Missions

### I've Hurt You (1 VP)

- **Printed goal:** Have 6 traits marked.
- **Goal check:** 6 or more of the 12 trait slots are marked.
- **Printed reward:** Take the top Encounter.
- **Reward steps:**
  1. Take the top Encounter.
- **Actions used:** `TAKE_ENCOUNTER`
- **Undoable:** no

### I Shall Leave You as You Left Me (2 VP)

- **Printed goal:** Have 9 traits marked.
- **Goal check:** 9 or more trait slots are marked.
- **Printed reward:** Look at the top 2 Encounter, take one of them and return the other to the bottom of its deck. Flip your Captain card.
- **Reward steps:**
  1. Look at the top 2 Encounters; take one and put the other on the bottom.
  2. Flip Khan's Captain card to Wrathful Khan (2KHA01B).
- **Actions used:** `TAKE_ENCOUNTER`, `FLIP_CARD`
- **Undoable:** no

### Marooned for All Eternity! Buried Alive! (3 VP)

- **Printed goal:** Have all 12 traits marked.
- **Goal check:** All 12 trait slots are marked.
- **Printed reward:** **ATTACK REWARD:** Force your opponent to recall a Person, if able, and log the recalled card.
- **Reward steps:**
  1. The opponent recalls one of their in-play Persons, choosing which (attack part).
  2. The opponent logs that card.
- **Attack:** yes. The reward targets the opponent (KW-ATK).
- **Actions used:** `ATTACK`, `FORCE`, `RECALL`, `LOG`
- **Undoable:** no

## Rulings and open questions

- Board rule printed on the scan: "After gaining a card or taking control of a Location that has one or more of the following traits, you *may* mark **one** of them as collected. (Wildcard counts as any one trait for this purpose.)" See REQ-CD-KHN-06.
- The 12 trait names are not visible in this scan; they are printed under the trait tokens. They must be transcribed before Khan can be played. Two of them depend on the opponent's Captain (REQ-CD-KHN-09).
- The second mission's reward flips the Captain. This is a second flip trigger besides Ceti Alpha VI; confirm whether both apply.

## Tests

- Given the goal is met, then the mission can be completed and its Mission Completion token placed (REQ-MS-06).
