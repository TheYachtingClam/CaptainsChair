---
id: 2KHA02B
name: Devastated Ceti Alpha V
suit: Location
set: to_boldly_go
deck: khan
set_code: 2KHA02B/22
position: null
traits: [Attack, Anomaly]
skills: []
focus: null
vp: null
away_teams: null
development_cost: null
ship_token: false
box_marker: null
scan: 2KHA02B.jpg
---

# Devastated Ceti Alpha V

## Printed text

> **ATTACK CONTROL:** Your opponent takes an Incident. Send all of your [Away Team] here.  
> **ACTIVATION:** If you have no [Away Team] here, draw a card.  
> **REACTION:** After putting an Augment into play, draw a card and you *may* enlist a Development.  
> **PASSIVE:** After returning an Incident, refresh this card.

## Operations

### 1. CONTROL

- **Printed:** Your opponent takes an Incident. Send all of your [Away Team] here.
- **Action cost:** no
- **Attack:** yes
- **Requires:** none
- **Cost:** none
- **Effect:**
  1. The opponent takes an Incident (attack part).
  2. Move every Away Team on Khan's Captain to this Location.
- **Actions used:** `ATTACK`, `TAKE_INCIDENT`, `SEND_AWAY_TEAM`
- **Undoable:** no

### 2. ACTIVATION

- **Printed:** If you have no [Away Team] here, draw a card.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Effect:**
  1. If none of your Away Teams are here, draw a card.
- **Actions used:** `DRAW`
- **Undoable:** no

### 3. REACTION

- **Printed:** After putting an Augment into play, draw a card and you may enlist a Development.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Trigger:** You put an Augment into play.
- **Effect:**
  1. Draw a card.
  2. You may enlist a Development, paying its cost.
- **Actions used:** `DRAW`, `ENLIST_DEVELOPMENT`
- **Undoable:** no

### 4. PASSIVE

- **Printed:** After returning an Incident, refresh this card.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Trigger:** You return an Incident.
- **Effect:**
  1. Refresh this Location.
- **Actions used:** `REFRESH`
- **Undoable:** yes

## Scoring

None.

## Solo

The Bot ignores the printed text and resolves this card through its Automated Command cards, by trait and then suit (REQ-SOLO-82).

## Rulings and open questions

- One side of a double-sided card. The card starts with its A side up; the B side is hidden until the card flips (REQ-CD-KHN-01).
- Its CONTROL is triggered by Ceti Alpha VI's RESUPPLY when the card flips.
- Khan's main way to enlist Developments (REQ-CD-KHN-03).

## Tests

- When its control resolves, then: The opponent takes an Incident (attack part). Move every Away Team on Khan's Captain to this Location.
- When its activation resolves, then: If none of your Away Teams are here, draw a card.
- When its reaction triggers (you put an augment into play), then: Draw a card. You may enlist a Development, paying its cost.
- When its passive triggers (you return an incident), then: Refresh this Location.
