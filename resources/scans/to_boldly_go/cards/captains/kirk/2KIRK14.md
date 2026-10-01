---
id: 2KIRK14
name: Analyze
suit: Directive
set: to_boldly_go
deck: kirk
set_code: 2KIRK14/25
position: Reserve
traits: []
skills: []
focus: null
vp: null
away_teams: null
development_cost: null
ship_token: false
box_marker: null
scan: 2KIRK14.jpg
---

# Analyze

## Printed text

> [Action] **PLAY:** Take an Incident to gain a Ship.  
> [Action] **PLAY:** Discard 2 cards to gain a Cargo.  
> **PLAY:** Gain 2 [Dilithium].

## Operations

### 1. PLAY

- **Printed:** Take an Incident to gain a Ship.
- **Action cost:** yes
- **Attack:** no
- **Requires:** none
- **Cost:** take an Incident
- **Effect:**
  1. Gain a Ship.
- **Actions used:** `TAKE_INCIDENT`, `GAIN_CARD`
- **Undoable:** no
- **Rules:** KW-TAKE, KW-GAIN

### 2. PLAY

- **Printed:** Discard 2 cards to gain a Cargo.
- **Action cost:** yes
- **Attack:** no
- **Requires:** none
- **Cost:** discard 2 cards
- **Effect:**
  1. Gain a Cargo.
- **Actions used:** `DISCARD`, `GAIN_CARD`
- **Undoable:** no
- **Rules:** KW-DIS, KW-GAIN

### 3. PLAY

- **Printed:** Gain 2 [Dilithium].
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Effect:**
  1. Gain 2 Dilithium.
- **Actions used:** `GAIN_RESOURCE`
- **Undoable:** yes
- **Rules:** KW-GRES

## Scoring

None.

## Solo

The Bot ignores the printed text and resolves this card through its Automated Command cards, by trait and then suit (REQ-SOLO-82).

## Rulings and open questions

- Common starting Directive. The same card appears in other Crew decks.

## Tests

- Given fewer than 2 other cards in hand, then the second PLAY cannot be played.
- The third PLAY costs no action.
- When its play resolves, then: Gain a Ship.
- Given the player cannot take an Incident, then this PLAY is not offered.
- When its play resolves, then: Gain a Cargo.
- Given the player cannot discard 2 cards, then this PLAY is not offered.
- When its play resolves, then: Gain 2 Dilithium.
