---
id: 2KHA01A
name: Khan Noonien Singh
suit: Captain
set: to_boldly_go
deck: khan
set_code: 2KHA01A/22
position: null
traits: [Human, Augment]
skills: []
focus: null
vp: null
away_teams: 4
development_cost: null
ship_token: false
box_marker: null
scan: 2KHA01A.jpg
---

# Khan Noonien Singh

Khan's Captain card, normal side. Flips to Wrathful Khan (2KHA01B) when Ceti Alpha VI is logged.

## Printed text

> **ACTIVATION:** Discard an Incident to draw 2 cards and discard one of them.  
> **PASSIVE:** After your opponent returns an Incident discard a card to gain 1 [Dilithium]/[Latinum].  
> **PASSIVE:** You do not enlist when you cycle your deck.

## Operations

### 1. ACTIVATION

- **Printed:** Discard an Incident to draw 2 cards and discard one of them.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** discard an Incident
- **Effect:**
  1. Draw 2 cards.
  2. Discard one of them.
- **Actions used:** `DISCARD`, `DRAW`
- **Undoable:** no

### 2. PASSIVE

- **Printed:** After your opponent returns an Incident discard a card to gain 1 [Dilithium]/[Latinum].
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Trigger:** The opponent returns an Incident.
- **Effect:**
  1. Discard a card to gain 1 Dilithium or 1 Latinum.
- **Actions used:** `DISCARD`, `GAIN_RESOURCE`
- **Undoable:** yes

### 3. PASSIVE

- **Printed:** You do not enlist when you cycle your deck.
- **Action cost:** no
- **Attack:** no
- **Requires:** none
- **Cost:** none
- **Effect:**
  1. Modifier: no Reserve or Development is enlisted when Khan's Draw deck is reshuffled (REQ-CD-KHN-03).

## Scoring

None.

## Solo

The Bot ignores the printed text and resolves this card through its Automated Command cards, by trait and then suit (REQ-SOLO-82).

## Rulings and open questions

- One side of a double-sided card. The card starts with its A side up; the B side is hidden until the card flips (REQ-CD-KHN-01).
- The second Passive is mandatory but has a cost; if Khan has no card in hand, it does nothing.
- Before the flip Khan has no Specialty tracks and cannot meet Specialty requirements (REQ-CD-KHN-04).

## Tests

- When its activation resolves, then: Draw 2 cards. Discard one of them.
- Given the player cannot discard an Incident, then this ACTIVATION is not offered.
- When its passive triggers (the opponent returns an incident), then: Discard a card to gain 1 Dilithium or 1 Latinum.
