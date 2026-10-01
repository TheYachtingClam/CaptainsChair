---
id: 2KIRK12
name: "Montgomery \"Scotty\" Scott"
suit: Person
set: to_boldly_go
deck: kirk
set_code: 2KIRK12/25
position: Reserve
traits: [Human, Engineer, Starfleet]
skills: []
focus: null
vp: null
away_teams: null
development_cost: null
ship_token: false
box_marker: null
scan: 2KIRK12.jpg
---

# Montgomery "Scotty" Scott

## Printed text

> **PLAY:** Find a Ship. If the card was found in your Reserve deck, take an Incident.  
> [Action] **PLAY:** Dismiss a deployed Ship to trigger a controlled Location's control operation and draw a card.  
> **ACTIVATION:** Gain 2 [Dilithium]. Refresh a Ship/Cargo.

## Operations

### 1. PLAY

- **Printed:** Find a Ship. If the card was found in your Reserve deck, take an Incident.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Effect:**
  1. Find a Ship.
  2. If it came from the Reserve deck, take an Incident.
- **Actions used:** `FIND`, `TAKE_INCIDENT`
- **Undoable:** no

### 2. PLAY

- **Printed:** Dismiss a deployed Ship to trigger a controlled Location's control operation and draw a card.
- **Action cost:** yes
- **Attack:** no
- **Requires:** none
- **Cost:** dismiss one of your deployed Ships
- **Effect:**
  1. Trigger one of your controlled Locations' CONTROL operation.
  2. Draw a card.
- **Actions used:** `DISMISS`, `TRIGGER_CONTROL`, `DRAW`
- **Undoable:** no

### 3. ACTIVATION

- **Printed:** Gain 2 [Dilithium]. Refresh a Ship/Cargo.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Effect:**
  1. Gain 2 Dilithium.
  2. Refresh one of your Ships or Cargo cards.
- **Actions used:** `GAIN_RESOURCE`, `REFRESH`
- **Undoable:** yes

## Scoring

None.

## Solo

The Bot ignores the printed text and resolves this card through its Automated Command cards, by trait and then suit (REQ-SOLO-82).

## Rulings and open questions

None.

## Tests

- When its play resolves, then: Find a Ship. If it came from the Reserve deck, take an Incident.
- When its play resolves, then: Trigger one of your controlled Locations' CONTROL operation. Draw a card.
- Given the player cannot dismiss one of your deployed Ships, then this PLAY is not offered.
- When its activation resolves, then: Gain 2 Dilithium. Refresh one of your Ships or Cargo cards.
