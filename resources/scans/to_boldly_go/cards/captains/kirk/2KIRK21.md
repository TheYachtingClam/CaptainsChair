---
id: 2KIRK21
name: Strange New Worlds
suit: Directive
set: to_boldly_go
deck: kirk
set_code: 2KIRK21/25
position: Available
traits: []
skills: []
focus: null
vp: null
away_teams: null
development_cost: null
ship_token: false
box_marker: null
scan: 2KIRK21.jpg
---

# Strange New Worlds

## Printed text

> [Action] **PLAY:** Select a controlled Location. If there is 1+ [Away Team] and 1+ Ship there, look at the top 2 Encounter. Take one of them and return the other to the bottom of its deck. Log the selected Location to gain 1 [Research].

## Operations

### 1. PLAY

- **Printed:** Select a controlled Location. If there is 1+ [Away Team] and 1+ Ship there, look at the top 2 Encounter. Take one of them and return the other to the bottom of its deck. Log the selected Location to gain 1 [Research].
- **Action cost:** yes
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Effect:**
  1. Choose one of your controlled Locations.
  2. If it has at least one of your Away Teams and one of your Ships: look at the top 2 Encounters, take one into hand, and put the other on the bottom of the Encounter deck.
  3. Log the chosen Location (its Ships are dismissed and Away Teams return) and gain 1 Research.
- **Actions used:** `TAKE_ENCOUNTER`, `LOG`, `GAIN_SPECIALTY`
- **Undoable:** no
- **Rules:** KW-TAKE, KW-LOG-04

## Scoring

None.

## Solo

The Bot ignores the printed text and resolves this card through its Automated Command cards, by trait and then suit (REQ-SOLO-82).

## Rulings and open questions

- Logging the selected Location is a required step, whether or not an Encounter was taken. Because a Location must be selected, the card cannot be played without a controlled Location.
- Rulebook reference (p. 8 and p. 34): the typical way Georgiou and Kirk get Encounters.

## Tests

- Given a controlled Location with an Away Team and a Ship, then the player takes one of the top 2 Encounters and the Location is logged.
- Given no Ship there, then no Encounter is taken but the Location is still logged.
- Given no controlled Location, then Strange New Worlds cannot be played.
- When its play resolves, then: Choose one of your controlled Locations. If it has at least one of your Away Teams and one of your Ships: look at the top 2 Encounters, take one into hand, and put the other on the bottom of the Encounter deck. Log the chosen Location (its Ships are dismissed and Away Teams return) and gain 1 Research.
