---
id: 2KIRK03
name: Starfleet Headquarters
suit: Location
set: to_boldly_go
deck: kirk
set_code: 2KIRK03/25
position: Controlled Location
traits: [Starfleet]
skills: [Any]
focus: null
vp: null
away_teams: null
development_cost: null
ship_token: false
box_marker: null
scan: 2KIRK03.jpg
---

# Starfleet Headquarters

## Printed text

> **SPECIAL:** When you log this card, up to X times, where X is the sequence number of the current Stardate card: send an [Away Team] to a Location.

## Operations

### 1. SPECIAL

- **Printed:** When you log this card, up to X times, where X is the sequence number of the current Stardate card: send an [Away Team] to a Location.
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Trigger:** You log Starfleet Headquarters.
- **Effect:**
  1. Send up to X Away Teams to Locations, where X is the current top Stardate card's sequence number.
- **Actions used:** `SEND_AWAY_TEAM`
- **Undoable:** yes

## Scoring

None.

## Solo

The Bot ignores the printed text and resolves this card through its Automated Command cards, by trait and then suit (REQ-SOLO-82).

## Rulings and open questions

- Starts in play as a controlled Location. It has no CONTROL or Activation; its value is the Any Skill icon and the logging bonus.
- After the Resolution, the current Stardate card is the last one, so X is its sequence number (5 in two-player).

## Tests

- When its special triggers (you log starfleet headquarters), then: Send up to X Away Teams to Locations, where X is the current top Stardate card's sequence number.
