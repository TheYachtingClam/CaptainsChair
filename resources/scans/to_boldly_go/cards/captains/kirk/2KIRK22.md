---
id: 2KIRK22
name: Nyota Uhura
suit: Person
set: to_boldly_go
deck: kirk
set_code: 2KIRK22/25
position: Available
traits: [Human, Starfleet, Communication]
skills: [Influence]
focus: null
vp: null
away_teams: null
development_cost: null
ship_token: false
box_marker: null
scan: 2KIRK22.jpg
---

# Nyota Uhura

## Printed text

> [Action] **PLAY:** Spend 2 [Dilithium] to gain a Person/Ally.  
> [Action] **PLAY:** *Requires* [Influence] 5. Spend 2 [Dilithium] to gain an Alien, including from the Junk.  
> **ACTIVATION:** For each Different Species you have in play, excluding cards with Starfleet (max 3 times): you *may* spend 1 [Dilithium] to gain 1 [Glory].

## Operations

### 1. PLAY

- **Printed:** Spend 2 [Dilithium] to gain a Person/Ally.
- **Action cost:** yes
- **Attack:** no
- **Requires:** none
- **Cost:** spend 2 Dilithium
- **Effect:**
  1. Gain a Person or Ally.
- **Actions used:** `GAIN_CARD`
- **Undoable:** no

### 2. PLAY

- **Printed:** Requires [Influence] 5. Spend 2 [Dilithium] to gain an Alien, including from the Junk.
- **Action cost:** yes
- **Attack:** no
- **Requires:** Influence track at 5 or more
- **Cost:** spend 2 Dilithium
- **Effect:**
  1. Gain an Alien from the Market or the Junk.
- **Actions used:** `GAIN_CARD`
- **Undoable:** no

### 3. ACTIVATION

- **Printed:** For each Different Species you have in play, excluding cards with Starfleet (max 3 times): you may spend 1 [Dilithium] to gain 1 [Glory].
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Effect:**
  1. For each different species among your in-play non-Starfleet cards, up to 3 times, you may spend 1 Dilithium to gain 1 Glory.
- **Actions used:** `SPEND`, `GAIN_RESOURCE`
- **Undoable:** yes

## Scoring

None.

## Solo

The Bot ignores the printed text and resolves this card through its Automated Command cards, by trait and then suit (REQ-SOLO-82).

## Rulings and open questions

None.

## Tests

- When its play resolves, then: Gain a Person or Ally.
- Given the player cannot spend 2 Dilithium, then this PLAY is not offered.
- When its play resolves, then: Gain an Alien from the Market or the Junk.
- Given the player cannot spend 2 Dilithium, then this PLAY is not offered.
- Given the requirement is not met (Influence track at 5 or more), then this PLAY is not offered.
- When its activation resolves, then: For each different species among your in-play non-Starfleet cards, up to 3 times, you may spend 1 Dilithium to gain 1 Glory.
