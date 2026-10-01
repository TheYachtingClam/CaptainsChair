---
id: 2KIRK07
name: Hikaru Sulu
suit: Person
set: to_boldly_go
deck: kirk
set_code: 2KIRK07/25
position: Development
traits: [Pilot, Human, Starfleet]
skills: [Military]
focus: null
vp: 2
away_teams: null
development_cost: "[Dilithium] x2"
ship_token: false
box_marker: null
scan: 2KIRK07.jpg
---

# Hikaru Sulu

## Printed text

> [Action] **PLAY:** Take an Incident to your Discard pile. Send 2 [Away Team] to a Location where you have a Ship.  
> **REACTION:** When you would be attacked, exhaust a Ship to ignore the negative effect.  
> **DEV. COST:** [Dilithium] x2

## Operations

### 1. PLAY

- **Printed:** Take an Incident to your Discard pile. Send 2 [Away Team] to a Location where you have a Ship.
- **Action cost:** yes
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Effect:**
  1. Take an Incident, putting it in your Discard pile.
  2. Send 2 Away Teams to a Location where you have a Ship.
- **Actions used:** `TAKE_INCIDENT`, `SEND_AWAY_TEAM`
- **Undoable:** no

### 2. REACTION

- **Printed:** When you would be attacked, exhaust a Ship to ignore the negative effect.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** exhaust one of your Ships
- **Trigger:** An opponent's attack is about to affect you (REQ-AS-27).
- **Effect:**
  1. Ignore the attack's negative effect.
- **Actions used:** `EXHAUST`
- **Undoable:** yes

### 3. DEVELOPMENT COST

- **Printed:** [Dilithium] x2
- **Effect:**
  1. Spend 2 Dilithium.
- **Rules:** KW-ENDEV

## Scoring

- Printed VP: 2.

## Solo

The Bot ignores the printed text and resolves this card through its Automated Command cards, by trait and then suit (REQ-SOLO-82).

## Rulings and open questions

None.

## Tests

- When its play resolves, then: Take an Incident, putting it in your Discard pile. Send 2 Away Teams to a Location where you have a Ship.
- When its reaction triggers (an opponent's attack is about to affect you (req-as-27)), then: Ignore the attack's negative effect.
- Given the player cannot exhaust one of your Ships, then this REACTION is not offered.
