---
id: 2KIRK24
name: Captain Spock
suit: Person
set: to_boldly_go
deck: kirk
set_code: 2KIRK24/25
position: Available
traits: [Human, Vulcan, Telepath, Scientist, Starfleet]
skills: [Research]
focus: null
vp: null
away_teams: null
development_cost: null
ship_token: false
box_marker: null
scan: 2KIRK24.jpg
---

# Captain Spock

## Printed text

> [Action] **PLAY:** Log a card from your hand or Discard pile to gain 3 [Dilithium]. If the logged card has 1+ [Research]/[Influence]/[Military]/[Research Focus]/[Influence Focus]/[Military Focus], gain 1 on the matching Specialty track (choose one if multiple, or if it has [Any Skill]/[Best Focus]).  
> **REACTION:** After gaining a Person, spend 1 [Dilithium] to send an [Away Team] to a Location where you have a Ship. If you do, gain 1 [Glory].

## Operations

### 1. PLAY

- **Printed:** Log a card from your hand or Discard pile to gain 3 [Dilithium]. If the logged card has 1+ Skill or Focus icons, gain 1 on the matching Specialty track (choose one if multiple, or if it has Any Skill/Best Focus).
- **Action cost:** yes
- **Attack:** no
- **Requires:** none
- **Cost:** log a card from hand or Discard pile
- **Effect:**
  1. Gain 3 Dilithium.
  2. If the logged card has any Skill or Focus icon, gain 1 on the matching track; choose if several match or the icon is Any Skill or Best Focus.
- **Actions used:** `LOG`, `GAIN_RESOURCE`, `GAIN_SPECIALTY`
- **Undoable:** yes

### 2. REACTION

- **Printed:** After gaining a Person, spend 1 [Dilithium] to send an [Away Team] to a Location where you have a Ship. If you do, gain 1 [Glory].
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** spend 1 Dilithium
- **Trigger:** You gain a Person.
- **Effect:**
  1. Send an Away Team to a Location where you have a Ship.
  2. Gain 1 Glory.
- **Actions used:** `SEND_AWAY_TEAM`, `GAIN_RESOURCE`
- **Undoable:** yes

## Scoring

None.

## Solo

The Bot ignores the printed text and resolves this card through its Automated Command cards, by trait and then suit (REQ-SOLO-82).

## Rulings and open questions

None.

## Tests

- When its play resolves, then: Gain 3 Dilithium. If the logged card has any Skill or Focus icon, gain 1 on the matching track; choose if several match or the icon is Any Skill or Best Focus.
- Given the player cannot log a card from hand or Discard pile, then this PLAY is not offered.
- When its reaction triggers (you gain a person), then: Send an Away Team to a Location where you have a Ship. Gain 1 Glory.
- Given the player cannot spend 1 Dilithium, then this REACTION is not offered.
