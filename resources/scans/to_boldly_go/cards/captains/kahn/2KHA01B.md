---
id: 2KHA01B
name: Wrathful Khan
suit: Captain
set: to_boldly_go
deck: khan
set_code: 2KHA01B/22
position: null
traits: [Human, Augment]
skills: []
focus: null
vp: null
away_teams: null
development_cost: null
ship_token: false
box_marker: null
scan: 2KHA01B.jpg
---

# Wrathful Khan

Khan's Captain card, flipped side. Away Teams on the Captain stay when it flips.

## Printed text

> **REACTION:** After your opponent returns an Incident, discard a card to gain 1 [Dilithium]/[Latinum].  
> **PASSIVE:** You do not enlist when you cycle your deck.  
> **PASSIVE:** Ignore all [Research]/[Influence]/[Military] requirements.  
> **ENDGAME:** Score 1 [VP] for each of your [Research Focus]/[Influence Focus]/[Military Focus]. If you have all 12 traits marked, score 3 [VP] for each instead.

## Operations

### 1. REACTION

- **Printed:** After your opponent returns an Incident, discard a card to gain 1 [Dilithium]/[Latinum].
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** discard a card
- **Trigger:** The opponent returns an Incident.
- **Effect:**
  1. Gain 1 Dilithium or 1 Latinum.
- **Actions used:** `DISCARD`, `GAIN_RESOURCE`
- **Undoable:** yes

### 2. PASSIVE

- **Printed:** You do not enlist when you cycle your deck.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Effect:**
  1. Modifier: no enlisting when the Draw deck is reshuffled.

### 3. PASSIVE

- **Printed:** Ignore all [Research]/[Influence]/[Military] requirements.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Effect:**
  1. Modifier: Khan meets every Specialty requirement (REQ-CD-KHN-04).

### 4. ENDGAME

- **Printed:** Score 1 [VP] for each of your Focus cards. If you have all 12 traits marked, score 3 [VP] for each instead.
- **Effect:**
  1. Score 1 VP per card you own with a Research, Influence or Military Focus icon; 3 VP each if all 12 board traits are marked (REQ-CD-KHN-05).

## Scoring

None.

## Solo

The Bot ignores the printed text and resolves this card through its Automated Command cards, by trait and then suit (REQ-SOLO-82).

## Rulings and open questions

- One side of a double-sided card. The card starts with its A side up; the B side is hidden until the card flips (REQ-CD-KHN-01).
- Wrathful Khan's Away Team count is not printed; the Away Teams from the A side carry over.

## Tests

- When its reaction triggers (the opponent returns an incident), then: Gain 1 Dilithium or 1 Latinum.
- Given the player cannot discard a card, then this REACTION is not offered.
