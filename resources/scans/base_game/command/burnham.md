---
id: burnham-command
name: Burnham Automated Command cards
suit: Automated Command
deck: burnham
set: base_game
sides:
  - burnham-traits   # burnham-traits.jpg
  - burnham-no-duty-officer   # burnham-no-duty-officer.jpg
  - burnham-with-duty-officer   # burnham-with-duty-officer.jpg
  - burnham-five-year-mission-upgrades   # burnham-five-year-mission-upgrades.jpg
---

# Burnham Automated Command cards

The Bot playing Burnham's Crew deck resolves every card with these rows instead of the card's own text (REQ-SOLO-80 to REQ-SOLO-83). Each row becomes one function in `server/engine/bot/burnham.py`, following the Bot action rules in CLAUDE.md.

## How a card is resolved

1. If the card has the Surprise trait, resolve its SURPRISE operation and stop (REQ-SOLO-87).
2. Otherwise check the TRAITS rows from top to bottom. The first row with a trait the card has is used. A Wildcard card matches the first trait row (REQ-SOLO-82).
3. If no trait row matches, use the row for the card's suit on whichever SUITS side is face up: WITH NO DUTY OFFICER, or WITH DUTY OFFICER.
4. "Continue resolution" stops the current row and finds the next matching row, trait rows first, then suits (REQ-SOLO-120).
5. A Location still in the Staging Area afterwards moves to the Bot's Control Area (REQ-SOLO-89).

Text shown **in bold** is resolved by the human player. On the card, bold red text is an attack, which the human may cancel; bold black text affects the human without attacking. Rows with an attack list the `ATTACK` action (REQ-SOLO-180 to REQ-SOLO-185).

## Special rule

During Clean-up Step, instead of adding [Glory], remove 1 [Glory] from the Stardate card and add 2 [Dilithium] to one Market card instead. At the end of the game, the Bot scores 1 [VP] per [Dilithium] (instead of the usual 1 [VP] per 2 [Dilithium]).

## TRAITS

Image id: `burnham-traits`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Surprise | Resolve this card's Surprise operation. | 1. Resolve the card's SURPRISE (Bot only) operation instead of any row. |  | yes |
| 2 | Creature | Gain 1 [Military]. Gain a Person / Cargo. If a Ship is in Bot Discard pile, deploy it; it explores. | 1. Gain 1 [Military].<br>2. Gain a Person / Cargo.<br>3. If a Ship is in Bot Discard pile, deploy it; it explores. | `GAIN_SPECIALTY`, `GAIN_CARD`, `DEPLOY`, `EXPLORE` | no |
| 3 | Scientist | Log the top card of the Bot deck. Take an Incident. Gain 1 [Research]. Gain an Ally. | 1. Log the top card of the Bot deck.<br>2. Take an Incident.<br>3. Gain 1 [Research].<br>4. Gain an Ally. | `LOG`, `TAKE_INCIDENT`, `GAIN_SPECIALTY`, `GAIN_CARD` | no |
| 4 | Anomaly | If a Person is in Bot Discard pile, promote it to Duty Officer. If this card is a Ship, deploy it; it explores. Otherwise, gain 2 [Glory]. | 1. If a Person is in Bot Discard pile, promote it to Duty Officer.<br>2. If this card is a Ship, deploy it; it explores.<br>3. Otherwise, gain 2 [Glory]. | `PROMOTE`, `DEPLOY`, `EXPLORE`, `GAIN_RESOURCE` | yes |
| 5 | Kelpien | If able, gain a Kelpien. Otherwise, gain the card in the Market with the most [Dilithium] > most [Glory]. If this card is a Person, promote it to Duty Officer. | 1. If able, gain a Kelpien.<br>2. Otherwise, gain the card in the Market with the most [Dilithium] > most [Glory].<br>3. If this card is a Person, promote it to Duty Officer. | `GAIN_CARD`, `PROMOTE` | no |

## SUITS WITH NO DUTY OFFICER

Image id: `burnham-no-duty-officer`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Discard the top card of the Bot deck. Gain 1 [Glory]. Gain a Scientist > Creature > Person. Return this card. | 1. Discard the top card of the Bot deck.<br>2. Gain 1 [Glory].<br>3. Gain a Scientist > Creature > Person.<br>4. Return this card. | `DISCARD`, `GAIN_RESOURCE`, `GAIN_CARD`, `RETURN_INCIDENT` | no |
| 2 | Ship | Deploy this Ship; it engages. Send an [Away Team] to a neutral Location. | 1. Deploy this Ship; it engages.<br>2. Send an [Away Team] to a neutral Location. | `DEPLOY`, `ENGAGE`, `SEND_AWAY_TEAM` | yes |
| 3 | Ally | Discard the top 3 cards of the Bot deck. Take an Incident. Gain 1 [Research]. | 1. Discard the top 3 cards of the Bot deck.<br>2. Take an Incident.<br>3. Gain 1 [Research]. | `DISCARD`, `TAKE_INCIDENT`, `GAIN_SPECIALTY` | no |
| 4 | Cargo | Gain the card in the Market with the most [Dilithium] > most [Glory]. Send an [Away Team] to a neutral Location. Log this card. | 1. Gain the card in the Market with the most [Dilithium] > most [Glory].<br>2. Send an [Away Team] to a neutral Location.<br>3. Log this card. | `GAIN_CARD`, `SEND_AWAY_TEAM`, `LOG` | no |
| 5 | Person | Gain 1 [Research]. Send an [Away Team] to a neutral Location. Promote this card to Duty Officer. | 1. Gain 1 [Research].<br>2. Send an [Away Team] to a neutral Location.<br>3. Promote this card to Duty Officer. | `GAIN_SPECIALTY`, `SEND_AWAY_TEAM`, `PROMOTE` | yes |
| 6 | Directive | Discard the top 2 cards of the Bot deck. Gain 2 [Influence]. Remove 1 [Glory] from the stardate card. | 1. Discard the top 2 cards of the Bot deck.<br>2. Gain 2 [Influence].<br>3. Remove 1 [Glory] from the stardate card. | `DISCARD`, `GAIN_SPECIALTY`, `REMOVE_STARDATE_GLORY` | yes |
| 7 | Encounter | Log the top 2 cards of the Bot deck. Take a Person. | 1. Log the top 2 cards of the Bot deck.<br>2. Take a Person. | `LOG`, `GAIN_CARD` | no |
| 8 | Location | Discard the top 2 cards of the Bot deck. Gain 1 [Military]. Gain 1 [Research] / [Influence] (whichever is lower). | 1. Discard the top 2 cards of the Bot deck.<br>2. Gain 1 [Military].<br>3. Gain 1 [Research] / [Influence] (whichever is lower). | `DISCARD`, `GAIN_SPECIALTY` | yes |

## SUITS WITH DUTY OFFICER

Image id: `burnham-with-duty-officer`.

Used while the Bot has a Duty Officer. Flip back when it is dismissed or logged (REQ-SOLO-91 to REQ-SOLO-95).

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Log the top card of the Bot deck. Gain 2 [Research]. Send an [Away Team] to a neutral Location. Return this card. | 1. Log the top card of the Bot deck.<br>2. Gain 2 [Research].<br>3. Send an [Away Team] to a neutral Location.<br>4. Return this card. | `LOG`, `GAIN_SPECIALTY`, `SEND_AWAY_TEAM`, `RETURN_INCIDENT` | yes |
| 2 | Ship | Gain 1 [Military]. Deploy this Ship; it explores. Send an [Away Team] to a neutral Location. | 1. Gain 1 [Military].<br>2. Deploy this Ship; it explores.<br>3. Send an [Away Team] to a neutral Location. | `GAIN_SPECIALTY`, `DEPLOY`, `EXPLORE`, `SEND_AWAY_TEAM` | yes |
| 3 | Ally | Discard the top 3 cards of the Bot deck. Gain 1 [Military]. Send an [Away Team] to a neutral Location. | 1. Discard the top 3 cards of the Bot deck.<br>2. Gain 1 [Military].<br>3. Send an [Away Team] to a neutral Location. | `DISCARD`, `GAIN_SPECIALTY`, `SEND_AWAY_TEAM` | yes |
| 4 | Cargo | Log the top card of the Bot deck. Gain a Ship. Log Duty Officer. | 1. Log the top card of the Bot deck.<br>2. Gain a Ship.<br>3. Log Duty Officer. | `LOG`, `GAIN_CARD` | no |
| 5 | Person | Discard the top 2 cards of Bot deck. Gain 1 [Research] / [Influence] (whichever is lower). Send an [Away Team] to a neutral Location. | 1. Discard the top 2 cards of Bot deck.<br>2. Gain 1 [Research] / [Influence] (whichever is lower).<br>3. Send an [Away Team] to a neutral Location. | `DISCARD`, `GAIN_SPECIALTY`, `SEND_AWAY_TEAM` | yes |
| 6 | Directive | If able to do both, log a controlled Location and remove an [Away Team] to gain top Encounter. Otherwise, discard the top 2 cards of the Bot deck and gain the card in the Market with the most [Dilithium] > most [Glory]. | 1. If able to do both, log a controlled Location and remove an [Away Team] to gain top Encounter.<br>2. Otherwise, discard the top 2 cards of the Bot deck and gain the card in the Market with the most [Dilithium] > most [Glory]. | `LOG`, `REMOVE_AWAY_TEAM`, `TAKE_ENCOUNTER`, `DISCARD`, `GAIN_CARD` | no |
| 7 | Encounter | Gain 1 [Research]. Gain 1 [Influence]. Gain a Scientist > Anomaly > Ship. Log this card. | 1. Gain 1 [Research].<br>2. Gain 1 [Influence].<br>3. Gain a Scientist > Anomaly > Ship.<br>4. Log this card. | `GAIN_SPECIALTY`, `GAIN_CARD`, `LOG` | no |
| 8 | Location | Log the top 2 cards of the Bot deck. Gain 1 [Research]. Dismiss Duty Officer. | 1. Log the top 2 cards of the Bot deck.<br>2. Gain 1 [Research].<br>3. Dismiss Duty Officer. | `LOG`, `GAIN_SPECIALTY`, `DISMISS` | yes |

## Five-Year Mission upgrades

Image id: `burnham-five-year-mission-upgrades`. Used only in the solo campaign (REQ-CAMP-25 to REQ-CAMP-31).

### WIN

- **A. Common card types you can reinforce:** Person / Creature
- **B. Alternative bonuses, pick 1:**
  - BOOST: After drawing the starting hand, draw 2 cards.
  - REINFORCE: A non-Incident card from your Reserve deck

### LOSS

- **A. Common card types you can reinforce:** Cargo / Starfleet / Person
- **B. Alternative bonuses, pick 1:**
  - BOOST: After drawing the starting hand, draw 1 card.
  - REINFORCE: A non-Incident card from your Available cards.

## Rulings and open questions

- The special rule is already REQ-SOLO-59 (Clean-up) and REQ-SOLO-72 (scoring). The Inert Dilithium Status card is removed when Burnham is the Bot (REQ-SOLO-26), so the Bot's Dilithium is never held back.
- 'The card in the Market with the most [Dilithium] > most [Glory]': the Market card with the most Dilithium on it; if none has Dilithium, the one with the most Glory; ties go to the most valuable, then the leftmost. It takes the tokens with the card.
- Directive row, no Duty Officer: 'Remove 1 [Glory] from the stardate card' returns it to the supply; the Bot does not gain it.
- "If able to do both, log ... and remove ... to take top Encounter" rows follow the same reading as the other Bots' Directive rows.

## Tests

- Given a card with a trait on the TRAITS side, when the Bot resolves it, then the first matching trait row is used.
- Given a card with no matching trait, when the Bot resolves it, then the row for its suit on the SUITS side face up is used.
