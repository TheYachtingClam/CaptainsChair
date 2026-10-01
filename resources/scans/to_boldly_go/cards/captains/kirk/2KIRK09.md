---
id: 2KIRK09
name: Vulcan
suit: Location
set: to_boldly_go
deck: kirk
set_code: 2KIRK09/25
position: Development
traits: [Vulcan]
skills: [Research, Research]
focus: Influence
vp: "?"
away_teams: null
development_cost: "[Dilithium] x4"
ship_token: false
box_marker: null
scan: 2KIRK09.jpg
---

# Vulcan

## Printed text

> [Action] **PLAY:** *Requires* [Research] 4. Take control of this location.  
> **CONTROL:** You *may* find a Vulcan. You *may* draw *Utilize* from your Discard pile. You *may* free play an Incident.  
> **ENDGAME:** Score [VP] equal to your highest multiplier on your Specialty ([Research]/[Influence]/[Military]) tracks.  
> **DEV. COST:** [Dilithium] x4

## Operations

### 1. PLAY

- **Printed:** Requires [Research] 4. Take control of this location.
- **Action cost:** yes
- **Attack:** no
- **Requires:** Research track at 4 or more
- **Cost:** none
- **Effect:**
  1. Take control of Vulcan.
- **Actions used:** `TAKE_CONTROL`
- **Undoable:** no

### 2. CONTROL

- **Printed:** You may find a Vulcan. You may draw Utilize from your Discard pile. You may free play an Incident.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Effect:**
  1. You may find a Vulcan.
  2. You may take Utilize from your Discard pile.
  3. You may free play an Incident.
- **Actions used:** `FIND`, `DRAW_FROM_DISCARD`, `FREE_PLAY`
- **Undoable:** no

### 3. ENDGAME

- **Printed:** Score [VP] equal to your highest multiplier on your Specialty tracks.
- **Effect:**
  1. Score VP equal to the highest multiplier reached on any track.

### 4. DEVELOPMENT COST

- **Printed:** [Dilithium] x4
- **Effect:**
  1. Spend 4 Dilithium.
- **Rules:** KW-ENDEV

## Scoring

- Printed VP: ?.
- Influence Focus: scores the highest Influence multiplier reached, only if at least one mission was completed (REQ-SP-11).

## Solo

The Bot ignores the printed text and resolves this card through its Automated Command cards, by trait and then suit (REQ-SOLO-82).

## Rulings and open questions

- Not the same card as Soval's starting Location Vulcan (2SOV03).

## Tests

- When its play resolves, then: Take control of Vulcan.
- Given the requirement is not met (Research track at 4 or more), then this PLAY is not offered.
- When its control resolves, then: You may find a Vulcan. You may take Utilize from your Discard pile. You may free play an Incident.
