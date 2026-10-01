---
id: 2KIRK04
name: What Have I Done
suit: Directive
set: to_boldly_go
deck: kirk
set_code: 2KIRK04/25
position: Development
traits: [Attack]
skills: []
focus: null
vp: 4
away_teams: null
development_cost: "[Latinum] x3"
ship_token: false
box_marker: null
scan: 2KIRK04.jpg
---

# What Have I Done

## Printed text

> [Action] **ATTACK PLAY:** Log a deployed Ship to send up to 3 [Away Team] to the same Location. If that Location is neutral and now secured, take control of it. Your opponent takes an Incident. Force your opponent to dismiss (one of) their Duty Officer(s). Log this card.  
> **DEV. COST:** [Latinum] x3

## Operations

### 1. PLAY

- **Printed:** Log a deployed Ship to send up to 3 [Away Team] to the same Location. If that Location is neutral and now secured, take control of it. Your opponent takes an Incident. Force your opponent to dismiss (one of) their Duty Officer(s). Log this card.
- **Action cost:** yes
- **Attack:** yes
- **Requires:** none
- **Cost:** log one of your deployed Ships that is at a Location
- **Effect:**
  1. Send up to 3 Away Teams to the logged Ship's Location.
  2. If that Location is neutral and you have now secured it, take control of it.
  3. The opponent takes an Incident (attack part).
  4. The opponent dismisses one of their Duty Officers (attack part).
  5. Log this card.
- **Actions used:** `LOG`, `SEND_AWAY_TEAM`, `TAKE_CONTROL`, `ATTACK`, `TAKE_INCIDENT`, `FORCE`, `DISMISS`
- **Undoable:** no

### 2. DEVELOPMENT COST

- **Printed:** [Latinum] x3
- **Effect:**
  1. Spend 3 Latinum.
- **Rules:** KW-ENDEV

## Scoring

- Printed VP: 4.

## Solo

The Bot ignores the printed text and resolves this card through its Automated Command cards, by trait and then suit (REQ-SOLO-82).

## Rulings and open questions

- The Ship's Location is taken before it is logged, since logging it removes its token.

## Tests

- When its play resolves, then: Send up to 3 Away Teams to the logged Ship's Location. If that Location is neutral and you have now secured it, take control of it. The opponent takes an Incident (attack part). The opponent dismisses one of their Duty Officers (attack part). Log this card.
- Given the player cannot log one of your deployed Ships that is at a Location, then this PLAY is not offered.
