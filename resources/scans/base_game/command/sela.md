---
id: sela-command
name: Sela Automated Command cards
suit: Automated Command
deck: sela
set: base_game
sides:
  - sela-traits   # sela-traits.jpg
  - sela-no-duty-officer   # sela-no-duty-officer.jpg
  - sela-with-duty-officer   # sela-with-duty-officer.jpg
  - sela-five-year-mission-upgrades   # sela-five-year-mission-upgrades.jpg
---

# Sela Automated Command cards

The Bot playing Sela's Crew deck resolves every card with these rows instead of the card's own text (REQ-SOLO-80 to REQ-SOLO-83). Each row becomes one function in `server/engine/bot/sela.py`, following the Bot action rules in CLAUDE.md.

## How a card is resolved

1. If the card has the Surprise trait, resolve its SURPRISE operation and stop (REQ-SOLO-87).
2. Otherwise check the TRAITS rows from top to bottom. The first row with a trait the card has is used. A Wildcard card matches the first trait row (REQ-SOLO-82).
3. If no trait row matches, use the row for the card's suit on whichever SUITS side is face up: WITH NO DUTY OFFICER, or WITH DUTY OFFICER.
4. "Continue resolution" stops the current row and finds the next matching row, trait rows first, then suits (REQ-SOLO-120).
5. A Location still in the Staging Area afterwards moves to the Bot's Control Area (REQ-SOLO-89).

Text shown **in bold** is resolved by the human player. On the card, bold red text is an attack, which the human may cancel; bold black text affects the human without attacking. Rows with an attack list the `ATTACK` action (REQ-SOLO-180 to REQ-SOLO-185).

## Special rule

None.

## TRAITS

Image id: `sela-traits`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Surprise | Resolve this card's Surprise operation. | 1. Resolve the card's SURPRISE (Bot only) operation instead of any row. |  | yes |
| 2 | Shady | Gain 1 [Military]. If able, gain a Klingon > Shady. If Bot has 8+ [Military], take control of the neutral Location with most Bot tokens (minimum 1) and log this card. If Bot has 7 or fewer [Military], gain 1 [Military] and 1 [Influence]. | 1. Gain 1 [Military].<br>2. If able, gain a Klingon > Shady.<br>3. If Bot has 8+ [Military], take control of the neutral Location with most Bot tokens (minimum 1) and log this card.<br>4. If Bot has 7 or fewer [Military], gain 1 [Military] and 1 [Influence]. | `GAIN_SPECIALTY`, `GAIN_CARD`, `TAKE_CONTROL`, `LOG` | no |
| 3 | Cloak | If this card is a Ship, send an [Away Team] to a neutral Location, ignoring any opponent Ship, and deploy this Ship; it engages. Otherwise, log this card and gain 3 [Glory]. | 1. If this card is a Ship, send an [Away Team] to a neutral Location, ignoring any opponent Ship, and deploy this Ship; it engages.<br>2. Otherwise, log this card and gain 3 [Glory]. | `SEND_AWAY_TEAM`, `DEPLOY`, `ENGAGE`, `LOG`, `GAIN_RESOURCE` | yes |
| 4 | Vulcan | Log the top card of the Bot deck. Gain 1 [Research] / [Influence] (whichever is lower). Gain a Klingon > Ship. If this card is a Person, promote it to Duty Officer. | 1. Log the top card of the Bot deck.<br>2. Gain 1 [Research] / [Influence] (whichever is lower).<br>3. Gain a Klingon > Ship.<br>4. If this card is a Person, promote it to Duty Officer. | `LOG`, `GAIN_SPECIALTY`, `GAIN_CARD`, `PROMOTE` | no |
| 5 | Klingon | Discard the top 2 cards of the Bot deck. Gain 2 [Influence] / [Military], whichever is lower. If this card is a Ship, then deploy this Ship; it explores. Otherwise, either **you dismiss a Ship** OR resolve the top card of the Bot deck. | 1. Discard the top 2 cards of the Bot deck.<br>2. Gain 2 [Influence] / [Military], whichever is lower.<br>3. If this card is a Ship, then deploy this Ship; it explores.<br>4. Otherwise, either you dismiss a Ship OR resolve the top card of the Bot deck. | `DISCARD`, `GAIN_SPECIALTY`, `DEPLOY`, `EXPLORE`, `ATTACK`, `DISMISS`, `RESOLVE_CARD` | no |
| 6 | Attack | Junk the most valuable card in the Market (ignoring any with tokens). Send an [Away Team] to a neutral Location. **You take an Incident OR dismiss (one of) your Duty Officer(s).** If Bot has 8+ [Military], log this card and either **you log a controlled Location OR discard a card.** | 1. Junk the most valuable card in the Market (ignoring any with tokens).<br>2. Send an [Away Team] to a neutral Location.<br>3. You take an Incident OR dismiss (one of) your Duty Officer(s).<br>4. If Bot has 8+ [Military], log this card and either you log a controlled Location OR discard a card. | `JUNK`, `SEND_AWAY_TEAM`, `ATTACK`, `TAKE_INCIDENT`, `DISMISS`, `LOG`, `DISCARD` | no |

## SUITS WITH NO DUTY OFFICER

Image id: `sela-no-duty-officer`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Gain 1 [Research] / [Influence] / [Military] (whichever is lower). Gain a Person / Ally. Return this card. | 1. Gain 1 [Research] / [Influence] / [Military] (whichever is lower).<br>2. Gain a Person / Ally.<br>3. Return this card. | `GAIN_SPECIALTY`, `GAIN_CARD`, `RETURN_INCIDENT` | no |
| 2 | Ship | Gain 1 [Military]. Deploy this Ship; it explores. | 1. Gain 1 [Military].<br>2. Deploy this Ship; it explores. | `GAIN_SPECIALTY`, `DEPLOY`, `EXPLORE` | yes |
| 3 | Ally | Discard the top 2 cards of the Bot deck. Gain a Klingon > Shady > Person. Send an [Away Team] to a neutral Location, ignoring any opponent Ship. **You may draw a card.** | 1. Discard the top 2 cards of the Bot deck.<br>2. Gain a Klingon > Shady > Person.<br>3. Send an [Away Team] to a neutral Location, ignoring any opponent Ship.<br>4. You may draw a card. | `DISCARD`, `GAIN_CARD`, `SEND_AWAY_TEAM`, `DRAW` | no |
| 4 | Cargo | Gain an Ally > Person. If Bot has 7+ [Military], gain 1 [Research] and 1 [Influence]. Otherwise, gain 2 [Glory] and 1 [Military]. | 1. Gain an Ally > Person.<br>2. If Bot has 7+ [Military], gain 1 [Research] and 1 [Influence].<br>3. Otherwise, gain 2 [Glory] and 1 [Military]. | `GAIN_CARD`, `GAIN_SPECIALTY`, `GAIN_RESOURCE` | no |
| 5 | Person | Gain 1 [Military]. If able, gain a Vulcan > Klingon. Otherwise, if able, dismiss a Ship to gain a Person / Ship. Otherwise, gain a Cargo. Promote this card to Duty Officer. | 1. Gain 1 [Military].<br>2. If able, gain a Vulcan > Klingon.<br>3. Otherwise, if able, dismiss a Ship to gain a Person / Ship.<br>4. Otherwise, gain a Cargo.<br>5. Promote this card to Duty Officer. | `GAIN_SPECIALTY`, `GAIN_CARD`, `DISMISS`, `PROMOTE` | no |
| 6 | Directive | Discard the top 3 cards of the Bot deck. Gain 2 [Research] / [Influence] / [Military] (whichever is lower). | 1. Discard the top 3 cards of the Bot deck.<br>2. Gain 2 [Research] / [Influence] / [Military] (whichever is lower). | `DISCARD`, `GAIN_SPECIALTY` | yes |
| 7 | Encounter | Resolve the top card of the Supplement deck. Log this card. | 1. Resolve the top card of the Supplement deck.<br>2. Log this card. | `RESOLVE_CARD`, `LOG` | no |
| 8 | Location | Log the top card of the Bot deck. Gain a Person and promote it to Duty Officer. | 1. Log the top card of the Bot deck.<br>2. Gain a Person and promote it to Duty Officer. | `LOG`, `GAIN_CARD`, `PROMOTE` | no |

## SUITS WITH DUTY OFFICER

Image id: `sela-with-duty-officer`.

Used while the Bot has a Duty Officer. Flip back when it is dismissed or logged (REQ-SOLO-91 to REQ-SOLO-95).

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Log the top card of the Bot deck. Gain 1 [Military]. Send an [Away Team] to a neutral Location. **You may draw a card.** Return this card. | 1. Log the top card of the Bot deck.<br>2. Gain 1 [Military].<br>3. Send an [Away Team] to a neutral Location.<br>4. You may draw a card.<br>5. Return this card. | `LOG`, `GAIN_SPECIALTY`, `SEND_AWAY_TEAM`, `DRAW`, `RETURN_INCIDENT` | no |
| 2 | Ship | Deploy this Ship; it engages. Send an [Away Team] to a neutral Location. | 1. Deploy this Ship; it engages.<br>2. Send an [Away Team] to a neutral Location. | `DEPLOY`, `ENGAGE`, `SEND_AWAY_TEAM` | yes |
| 3 | Ally | Discard the top 2 cards of the Bot deck. Take an Incident. Gain 2 [Research] / [Influence] / [Military] (whichever is lower), and **you take an Incident.** Dismiss Duty Officer. Log this card. | 1. Discard the top 2 cards of the Bot deck.<br>2. Take an Incident.<br>3. Gain 2 [Research] / [Influence] / [Military] (whichever is lower), and you take an Incident.<br>4. Dismiss Duty Officer.<br>5. Log this card. | `DISCARD`, `TAKE_INCIDENT`, `GAIN_SPECIALTY`, `ATTACK`, `DISMISS`, `LOG` | no |
| 4 | Cargo | Resolve the top card of the Supplement deck. Log Duty Officer. Log this card. | 1. Resolve the top card of the Supplement deck.<br>2. Log Duty Officer.<br>3. Log this card. | `RESOLVE_CARD`, `LOG` | no |
| 5 | Person | Log the top card of the Bot deck. Discard the top 3 cards of the Bot deck. If able, gain a Shady > Vulcan. Otherwise, gain 2 [Military]. | 1. Log the top card of the Bot deck.<br>2. Discard the top 3 cards of the Bot deck.<br>3. If able, gain a Shady > Vulcan.<br>4. Otherwise, gain 2 [Military]. | `LOG`, `DISCARD`, `GAIN_CARD`, `GAIN_SPECIALTY` | no |
| 6 | Directive | If able, remove 2 [Away Team] to gain top Encounter, then log this card and log Duty Officer. Otherwise, gain a Shady > Attack > Cargo / Ship. | 1. If able, remove 2 [Away Team] to gain top Encounter, then log this card and log Duty Officer.<br>2. Otherwise, gain a Shady > Attack > Cargo / Ship. | `REMOVE_AWAY_TEAM`, `TAKE_ENCOUNTER`, `LOG`, `GAIN_CARD` | no |
| 7 | Encounter | Gain 2 [Glory]. Send an [Away Team] to a neutral Location. Send an [Away Team] to a neutral Location. Log Duty Officer. Log this card. | 1. Gain 2 [Glory].<br>2. Send an [Away Team] to a neutral Location.<br>3. Send an [Away Team] to a neutral Location.<br>4. Log Duty Officer.<br>5. Log this card. | `GAIN_RESOURCE`, `SEND_AWAY_TEAM`, `LOG` | yes |
| 8 | Location | If able, gain a Shady. Otherwise, dismiss Duty Officer, gain a Person / Cargo / Ally, and **you discard a card.** | 1. If able, gain a Shady.<br>2. Otherwise, dismiss Duty Officer, gain a Person / Cargo / Ally, and you discard a card. | `GAIN_CARD`, `DISMISS`, `ATTACK`, `DISCARD` | no |

## Five-Year Mission upgrades

Image id: `sela-five-year-mission-upgrades`. Used only in the solo campaign (REQ-CAMP-25 to REQ-CAMP-31).

### WIN

- **A. Common card types you can reinforce:** Attack / Shady / Cloak
- **B. Alternative bonuses, pick 1:**
  - BOOST: Before drawing the starting hand, find a card (from your draw deck or Reserve) and log the found card.
  - BOOST: After drawing the starting hand, take a card from your Reinforcement deck.

### LOSS

- **A. Common card types you can reinforce:** Weapon / Attack / Romulan
- **B. Alternative bonuses, pick 1:**
  - REINFORCE: A non-Incident card from your Reserve deck
  - REINFORCE: A non-Incident card from your Available cards.

## Rulings and open questions

- Shady row: 'take control of the neutral Location with most Bot tokens (minimum 1)' takes it without securing it; the Bot then resolves it as a controlled Location (REQ-SOLO-52). Open question: whether the human's tokens there still earn them Glory.
- Klingon row: 'either you dismiss a Ship OR resolve the top card of the Bot deck' is the human's choice (REQ-SOLO-183); with no Ship to dismiss the Bot resolves the top card.
- Attack row: both 'OR' choices are the human's. The second pair applies only at 8+ Military.
- Directive row with a Duty Officer says 'gain top Encounter': it goes to the Bot Discard pile, not the Bot deck.
- "If able to do both, log ... and remove ... to take top Encounter" rows follow the same reading as the other Bots' Directive rows.

## Tests

- Given a card with a trait on the TRAITS side, when the Bot resolves it, then the first matching trait row is used.
- Given a card with no matching trait, when the Bot resolves it, then the row for its suit on the SUITS side face up is used.
