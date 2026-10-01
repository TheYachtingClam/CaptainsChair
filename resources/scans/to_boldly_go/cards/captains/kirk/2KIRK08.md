---
id: 2KIRK08
name: Sarek
suit: Person
set: to_boldly_go
deck: kirk
set_code: 2KIRK08/25
position: Development
traits: [Vulcan, Telepath, Ambassador]
skills: [Influence]
focus: null
vp: 2
away_teams: null
development_cost: "[Dilithium] x1, [Latinum] x1"
ship_token: false
box_marker: null
scan: 2KIRK08.jpg
---

# Sarek

## Printed text

> [Action] **PLAY:** Gain 1 [Influence] for each Vulcan you have in play (including this card). You *may* promote *Sarek* and optionally another Person from your Staging Area to Duty Officer(s).  
> **PASSIVE:** You *may* have up to two additional Person on duty.  
> **DEV. COST:** [Dilithium] x1, [Latinum] x1

## Operations

### 1. PLAY

- **Printed:** Gain 1 [Influence] for each Vulcan you have in play (including this card). You may promote Sarek and optionally another Person from your Staging Area to Duty Officer(s).
- **Action cost:** yes
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Effect:**
  1. Gain 1 Influence per Vulcan in play, counting Sarek.
  2. You may promote Sarek, and if you do, optionally one other Person from your Staging Area.
- **Actions used:** `GAIN_SPECIALTY`, `PROMOTE`
- **Undoable:** yes

### 2. PASSIVE

- **Printed:** You may have up to two additional Person on duty.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Effect:**
  1. Modifier: Duty Officer limit +2 while Sarek is on duty.
- **Rules:** KW-PROM-04

### 3. DEVELOPMENT COST

- **Printed:** [Dilithium] x1, [Latinum] x1
- **Effect:**
  1. Spend 1 Dilithium and 1 Latinum.
- **Rules:** KW-ENDEV

## Scoring

- Printed VP: 2.

## Solo

The Bot ignores the printed text and resolves this card through its Automated Command cards, by trait and then suit (REQ-SOLO-82).

## Rulings and open questions

- Same text as Georgiou's Ambassador Sarek (2GEO04), but named Sarek.

## Tests

- When its play resolves, then: Gain 1 Influence per Vulcan in play, counting Sarek. You may promote Sarek, and if you do, optionally one other Person from your Staging Area.
