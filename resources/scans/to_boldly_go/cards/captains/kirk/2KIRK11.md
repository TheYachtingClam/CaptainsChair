---
id: 2KIRK11
name: H.M.S. Bounty
suit: Ship
set: to_boldly_go
deck: kirk
set_code: 2KIRK11/25
position: Reserve
traits: [Cloak, Klingon]
skills: []
focus: null
vp: null
away_teams: null
development_cost: null
ship_token: true
box_marker: null
scan: 2KIRK11.jpg
---

# H.M.S. Bounty

## Printed text

> **PLAY:** Deploy this ship.  
> **PLAY:** *Requires* [Influence] 5. Deploy this ship. You *may* discard an Incident to send an [Away Team] to a Location, ignoring any opponent Ship.  
> **ACTIVATION:** Spend 1 [Dilithium] to warp this ship.  
> **ACTIVATION:** Discard a card to beam a card here.

## Operations

### 1. PLAY

- **Printed:** Deploy this ship.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Effect:**
  1. Deploy this Ship.
- **Actions used:** `DEPLOY`
- **Undoable:** yes

### 2. PLAY

- **Printed:** Requires [Influence] 5. Deploy this ship. You may discard an Incident to send an [Away Team] to a Location, ignoring any opponent Ship.
- **Action cost:** no
- **Attack:** no
- **Requires:** Influence track at 5 or more
- **Cost:** none
- **Effect:**
  1. Deploy this Ship.
  2. You may discard an Incident to send an Away Team to any Location, ignoring opponent Ships.
- **Actions used:** `DEPLOY`, `DISCARD`, `SEND_AWAY_TEAM`
- **Undoable:** yes
- **Rules:** KW-SEND-03

### 3. ACTIVATION

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

### 4. ACTIVATION

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

## Scoring

None.

## Solo

The Bot ignores the printed text and resolves this card through its Automated Command cards, by trait and then suit (REQ-SOLO-82).

## Rulings and open questions

None.

## Tests

- When its play resolves, then: Deploy this Ship.
- When its play resolves, then: Deploy this Ship. You may discard an Incident to send an Away Team to any Location, ignoring opponent Ships.
- Given the requirement is not met (Influence track at 5 or more), then this PLAY is not offered.
- When its activation resolves, then: Warp this Ship.
- Given the player cannot spend 1 Dilithium, then this ACTIVATION is not offered.
- When its activation resolves, then: Beam a card from hand to this Ship.
- Given the player cannot discard a card, then this ACTIVATION is not offered.
