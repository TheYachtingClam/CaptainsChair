---
id: 2KIRK23
name: Leonard McCoy
suit: Person
set: to_boldly_go
deck: kirk
set_code: 2KIRK23/25
position: Available
traits: [Human, Doctor, Starfleet]
skills: []
focus: null
vp: null
away_teams: null
development_cost: null
ship_token: false
box_marker: null
scan: 2KIRK23.jpg
---

# Leonard McCoy

## Printed text

> [Action] **PLAY:** Gain 1 [Research]. You *may* return an Incident.  
> **REACTION:** After discarding or logging a Person during your Action Step, free play an Incident from your hand or Discard pile.

## Operations

### 1. PLAY

- **Printed:** Gain 1 [Research]. You may return an Incident.
- **Action cost:** yes
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Effect:**
  1. Gain 1 Research.
  2. You may return an Incident from hand.
- **Actions used:** `GAIN_SPECIALTY`, `RETURN_INCIDENT`
- **Undoable:** yes

### 2. REACTION

- **Printed:** After discarding or logging a Person during your Action Step, free play an Incident from your hand or Discard pile.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Trigger:** You discard or log a Person during your Action Step.
- **Effect:**
  1. Free play an Incident from hand or Discard pile.
- **Actions used:** `FREE_PLAY`
- **Undoable:** yes

## Scoring

None.

## Solo

The Bot ignores the printed text and resolves this card through its Automated Command cards, by trait and then suit (REQ-SOLO-82).

## Rulings and open questions

None.

## Tests

- When its play resolves, then: Gain 1 Research. You may return an Incident from hand.
- When its reaction triggers (you discard or log a person during your action step), then: Free play an Incident from hand or Discard pile.
