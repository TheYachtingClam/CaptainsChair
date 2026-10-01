---
id: 2KIRK13
name: Pavel Chekov
suit: Person
set: to_boldly_go
deck: kirk
set_code: 2KIRK13/25
position: Reserve
traits: [Ops, Human, Attack, Starfleet]
skills: []
focus: null
vp: null
away_teams: null
development_cost: null
ship_token: false
box_marker: null
scan: 2KIRK13.jpg
---

# Pavel Chekov

## Printed text

> [Action] **ATTACK PLAY:** Discard the top card of your deck. Send an [Away Team] to a Location. If your opponent has at least one [Away Team] at the same Location, force them to discard a card.  
> **REACTION:** After warping a Ship to a neutral Location, discard a Person to send an [Away Team] to the same Location, and gain 1 [Glory].

## Operations

### 1. PLAY

- **Printed:** Discard the top card of your deck. Send an [Away Team] to a Location. If your opponent has at least one [Away Team] at the same Location, force them to discard a card.
- **Action cost:** yes
- **Attack:** yes
- **Requires:** none
- **Cost:** none
- **Effect:**
  1. Discard the top card of your Draw deck.
  2. Send an Away Team to a Location.
  3. If the opponent has an Away Team there, they discard a card (attack part).
- **Actions used:** `DISCARD`, `SEND_AWAY_TEAM`, `ATTACK`, `FORCE`
- **Undoable:** no

### 2. REACTION

- **Printed:** After warping a Ship to a neutral Location, discard a Person to send an [Away Team] to the same Location, and gain 1 [Glory].
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** discard a Person
- **Trigger:** You warp a Ship to a Neutral Zone Location.
- **Effect:**
  1. Send an Away Team to that Location.
  2. Gain 1 Glory.
- **Actions used:** `DISCARD`, `SEND_AWAY_TEAM`, `GAIN_RESOURCE`
- **Undoable:** yes

## Scoring

None.

## Solo

The Bot ignores the printed text and resolves this card through its Automated Command cards, by trait and then suit (REQ-SOLO-82).

## Rulings and open questions

None.

## Tests

- When its play resolves, then: Discard the top card of your Draw deck. Send an Away Team to a Location. If the opponent has an Away Team there, they discard a card (attack part).
- When its reaction triggers (you warp a ship to a neutral zone location), then: Send an Away Team to that Location. Gain 1 Glory.
- Given the player cannot discard a Person, then this REACTION is not offered.
