---
id: 2KIRK17
name: Levitation Boots
suit: Cargo
set: to_boldly_go
deck: kirk
set_code: 2KIRK17/25
position: Available
traits: [Ongoing]
skills: []
focus: null
vp: null
away_teams: null
development_cost: null
ship_token: false
box_marker: null
scan: 2KIRK17.jpg
---

# Levitation Boots

## Printed text

> **PLAY:** Deploy this card. You *may* beam up to 3 Person from your hand or Discard pile here.  
> **ACTIVATION:** Recall a Person beamed here.  
> **ACTIVATION:** Spend 1 [Dilithium] to beam a Person here from your hand or Discard pile.  
> **PASSIVE:** If no cards are beamed here, dismiss this card.

## Operations

### 1. PLAY

- **Printed:** Deploy this card. You may beam up to 3 Person from your hand or Discard pile here.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Effect:**
  1. Deploy this card.
  2. You may beam up to 3 Persons from hand or Discard pile to it.
- **Actions used:** `DEPLOY`, `BEAM`
- **Undoable:** yes

### 2. ACTIVATION

- **Printed:** Recall a Person beamed here.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Effect:**
  1. Recall a Person beamed to this card.
- **Actions used:** `RECALL`
- **Undoable:** yes

### 3. ACTIVATION

- **Printed:** Spend 1 [Dilithium] to beam a Person here from your hand or Discard pile.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** spend 1 Dilithium
- **Effect:**
  1. Beam a Person from hand or Discard pile here.
- **Actions used:** `BEAM`
- **Undoable:** yes

### 4. PASSIVE

- **Printed:** If no cards are beamed here, dismiss this card.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Trigger:** Levitation Boots is deployed with no cards beamed to it.
- **Effect:**
  1. Dismiss this card whenever it has no beamed cards.
- **Actions used:** `DISMISS`
- **Undoable:** yes

## Scoring

None.

## Solo

The Bot ignores the printed text and resolves this card through its Automated Command cards, by trait and then suit (REQ-SOLO-82).

## Rulings and open questions

- The Passive is checked after the PLAY finishes, so deploying with nothing beamed dismisses it at once.

## Tests

- When its play resolves, then: Deploy this card. You may beam up to 3 Persons from hand or Discard pile to it.
- When its activation resolves, then: Recall a Person beamed to this card.
- When its activation resolves, then: Beam a Person from hand or Discard pile here.
- Given the player cannot spend 1 Dilithium, then this ACTIVATION is not offered.
- When its passive triggers (levitation boots is deployed with no cards beamed to it), then: Dismiss this card whenever it has no beamed cards.
