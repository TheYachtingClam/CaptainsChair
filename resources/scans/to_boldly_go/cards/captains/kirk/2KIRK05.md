---
id: 2KIRK05
name: U.S.S. Enterprise-A
suit: Ship
set: to_boldly_go
deck: kirk
set_code: 2KIRK05/25
position: Development
traits: [Starfleet]
skills: [Any, Any]
focus: null
vp: 4
away_teams: null
development_cost: "[Dilithium] x6 OR free if the U.S.S. Enterprise (Refit) is logged."
ship_token: true
box_marker: null
scan: 2KIRK05.jpg
---

# U.S.S. Enterprise-A

## Printed text

> [Action] **PLAY:** Deploy this ship. Warp this ship **OR** beam a card here. You *may* discard a card to beam a (different) card here.  
> **ACTIVATION:** Spend 1 [Dilithium] to warp this ship.  
> **ACTIVATION:** Discard a card to beam a card here.  
> **ACTIVATION:** Promote a Person from your hand to Duty Officer.  
> **DEV. COST:** [Dilithium] x6 **OR** free if the *U.S.S. Enterprise (Refit)* is logged.

## Operations

### 1. PLAY

- **Printed:** Deploy this ship. Warp this ship OR beam a card here. You may discard a card to beam a (different) card here.
- **Action cost:** yes
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Effect:**
  1. Deploy this Ship.
  2. Choose: warp it, or beam a card from hand to it.
  3. You may discard a card to beam another card from hand to it.
- **Actions used:** `DEPLOY`, `WARP`, `BEAM`, `DISCARD`
- **Undoable:** yes

### 2. ACTIVATION

- **Printed:** Spend 1 [Dilithium] to warp this ship.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** spend 1 Dilithium
- **Effect:**
  1. Warp this Ship.
- **Actions used:** `WARP`
- **Undoable:** yes
- **Rules:** KW-WARP

### 3. ACTIVATION

- **Printed:** Discard a card to beam a card here.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** discard a card
- **Effect:**
  1. Beam a card from hand to this Ship.
- **Actions used:** `DISCARD`, `BEAM`
- **Undoable:** yes
- **Rules:** KW-BEAM

### 4. ACTIVATION

- **Printed:** Promote a Person from your hand to Duty Officer.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Effect:**
  1. Promote a Person from your hand.
- **Actions used:** `PROMOTE`
- **Undoable:** yes

### 5. DEVELOPMENT COST

- **Printed:** [Dilithium] x6 OR free if the U.S.S. Enterprise (Refit) is logged.
- **Effect:**
  1. Spend 6 Dilithium; or pay nothing if 2KIRK02 is in your Log.
- **Rules:** KW-ENDEV

## Scoring

- Printed VP: 4.

## Solo

The Bot ignores the printed text and resolves this card through its Automated Command cards, by trait and then suit (REQ-SOLO-82).

## Rulings and open questions

None.

## Tests

- When its play resolves, then: Deploy this Ship. Choose: warp it, or beam a card from hand to it. You may discard a card to beam another card from hand to it.
- When its activation resolves, then: Warp this Ship.
- Given the player cannot spend 1 Dilithium, then this ACTIVATION is not offered.
- When its activation resolves, then: Beam a card from hand to this Ship.
- Given the player cannot discard a card, then this ACTIVATION is not offered.
- When its activation resolves, then: Promote a Person from your hand.
