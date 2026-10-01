---
id: 2KIRK01
name: James T. Kirk
suit: Captain
set: to_boldly_go
deck: kirk
set_code: 2KIRK01/25
position: null
traits: [Human, Starfleet]
skills: []
focus: null
vp: null
away_teams: 5
development_cost: null
ship_token: false
box_marker: null
scan: 2KIRK01.jpg
---

# James T. Kirk

Kirk's Captain card. Starts with 5 Away Teams.

## Printed text

> **REACTION:** After putting a Klingon into play, discard a card to gain 1 [Military].  
> **ACTIVATION:** Put a card on the top of your deck to draw a Directive from your Discard pile.  
> **ENDGAME:** Score 1 [VP] for every second step gained on [Research]/[Influence]/[Military], whichever is the lowest.

## Operations

### 1. REACTION

- **Printed:** After putting a Klingon into play, discard a card to gain 1 [Military].
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** discard a card
- **Trigger:** You put a Klingon card into play.
- **Effect:**
  1. Gain 1 Military.
- **Actions used:** `DISCARD`, `GAIN_SPECIALTY`
- **Undoable:** yes

### 2. ACTIVATION

- **Printed:** Put a card on the top of your deck to draw a Directive from your Discard pile.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** put a card from hand on top of your Draw deck
- **Effect:**
  1. Take a Directive from your Discard pile.
- **Actions used:** `PUT`, `DRAW_FROM_DISCARD`
- **Undoable:** yes

### 3. ENDGAME

- **Printed:** Score 1 [VP] for every second step gained on [Research]/[Influence]/[Military], whichever is the lowest.
- **Effect:**
  1. Take your lowest Specialty track position and score 1 VP per full 2 steps.

## Scoring

None.

## Solo

The Bot ignores the printed text and resolves this card through its Automated Command cards, by trait and then suit (REQ-SOLO-82).

## Rulings and open questions

- The ENDGAME uses current track positions, not multipliers.

## Tests

- When its reaction triggers (you put a klingon card into play), then: Gain 1 Military.
- Given the player cannot discard a card, then this REACTION is not offered.
- When its activation resolves, then: Take a Directive from your Discard pile.
- Given the player cannot put a card from hand on top of your Draw deck, then this ACTIVATION is not offered.
