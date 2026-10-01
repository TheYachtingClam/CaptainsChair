---
id: 2KIRK06
name: U.S.S. Excelsior
suit: Ship
set: to_boldly_go
deck: kirk
set_code: 2KIRK06/25
position: Development
traits: [Attack, Starfleet]
skills: [Any, Any]
focus: Military
vp: "?"
away_teams: null
development_cost: "[Dilithium] x6 OR free if Hikaru Sulu is your Duty Officer."
ship_token: true
box_marker: null
scan: 2KIRK06.jpg
---

# U.S.S. Excelsior

## Printed text

> [Action] **ATTACK PLAY:** Deploy this ship. If the opponent has at least one Ship at a neutral Location, they take an Incident. You *may* find *Set a Course*.  
> **ACTIVATION:** Spend 1 [Dilithium] to warp this ship.  
> **ACTIVATION:** Discard a card to beam a card here.  
> **ACTIVATION:** Spend 1 [Dilithium] to recall this ship.  
> **DEV. COST:** [Dilithium] x6 **OR** free if *Hikaru Sulu* is your Duty Officer.

## Operations

### 1. PLAY

- **Printed:** Deploy this ship. If the opponent has at least one Ship at a neutral Location, they take an Incident. You may find Set a Course.
- **Action cost:** yes
- **Attack:** yes
- **Requires:** none
- **Cost:** none
- **Effect:**
  1. Deploy this Ship.
  2. If the opponent has a Ship at a neutral Location, they take an Incident (attack part).
  3. You may find Set a Course (2KIRK20).
- **Actions used:** `DEPLOY`, `ATTACK`, `TAKE_INCIDENT`, `FIND`
- **Undoable:** no

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

- **Printed:** Spend 1 [Dilithium] to recall this ship.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** spend 1 Dilithium
- **Effect:**
  1. Recall the Excelsior to hand, with its beamed cards.
- **Actions used:** `RECALL`
- **Undoable:** yes

### 5. DEVELOPMENT COST

- **Printed:** [Dilithium] x6 OR free if Hikaru Sulu is your Duty Officer.
- **Effect:**
  1. Spend 6 Dilithium; or pay nothing if Hikaru Sulu (2KIRK07) is on duty.
- **Rules:** KW-ENDEV

## Scoring

- Printed VP: ?.
- Military Focus: scores the highest Military multiplier reached, only if at least one mission was completed (REQ-SP-11).

## Solo

The Bot ignores the printed text and resolves this card through its Automated Command cards, by trait and then suit (REQ-SOLO-82).

## Rulings and open questions

- Recalling lets the attack PLAY be used again on a later turn.

## Tests

- When its play resolves, then: Deploy this Ship. If the opponent has a Ship at a neutral Location, they take an Incident (attack part). You may find Set a Course (2KIRK20).
- When its activation resolves, then: Warp this Ship.
- Given the player cannot spend 1 Dilithium, then this ACTIVATION is not offered.
- When its activation resolves, then: Beam a card from hand to this Ship.
- Given the player cannot discard a card, then this ACTIVATION is not offered.
- When its activation resolves, then: Recall the Excelsior to hand, with its beamed cards.
- Given the player cannot spend 1 Dilithium, then this ACTIVATION is not offered.
