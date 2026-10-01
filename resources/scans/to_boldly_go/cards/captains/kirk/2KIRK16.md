---
id: 2KIRK16
name: Subspace Phenomenon
suit: Incident
set: to_boldly_go
deck: kirk
set_code: 2KIRK16/25
position: Available
traits: []
skills: []
focus: null
vp: -2
away_teams: null
development_cost: null
ship_token: false
box_marker: null
scan: 2KIRK16.jpg
---

# Subspace Phenomenon

## Printed text

> [Action] **PLAY:** Discard a card to return this card. If the discarded card has [Research]/[Research Focus], draw 2 cards and discard one of them.  
> [Action] **PLAY:** If you have a Time Travel in play, return this card and draw 2 cards and discard one of them.

## Operations

### 1. PLAY

- **Printed:** Discard a card to return this card. If the discarded card has [Research]/[Research Focus], draw 2 cards and discard one of them.
- **Action cost:** yes
- **Attack:** no
- **Requires:** none
- **Cost:** discard a card
- **Effect:**
  1. Return this card.
  2. If the discarded card has a Research Skill or Focus icon, draw 2 cards and discard one of them.
- **Actions used:** `DISCARD`, `RETURN_INCIDENT`, `DRAW`
- **Undoable:** no
- **Rules:** KW-RETI

### 2. PLAY

- **Printed:** If you have a Time Travel in play, return this card and draw 2 cards and discard one of them.
- **Action cost:** yes
- **Attack:** no
- **Requires:** a Time Travel card in play
- **Cost:** none
- **Effect:**
  1. Return this card.
  2. Draw 2 cards and discard one of them.
- **Actions used:** `RETURN_INCIDENT`, `DRAW`, `DISCARD`
- **Undoable:** no
- **Rules:** KW-RETI

## Scoring

- Printed VP: -2.

## Solo

The Bot ignores the printed text and resolves this card through its Automated Command cards, by trait and then suit (REQ-SOLO-82).

## Rulings and open questions

- Incidents count toward the Burn while owned (REQ-OV-23) and score their negative VP at game end.

## Tests

- When its play resolves, then: Return this card. If the discarded card has a Research Skill or Focus icon, draw 2 cards and discard one of them.
- Given the player cannot discard a card, then this PLAY is not offered.
- When its play resolves, then: Return this card. Draw 2 cards and discard one of them.
- Given the requirement is not met (a Time Travel card in play), then this PLAY is not offered.
