---
id: riker-command
name: Riker Automated Command cards
suit: Automated Command
deck: riker
set: second_contact
sides:
  - riker-traits   # riker-traits.jpg
  - riker-no-duty-officer   # riker-no-duty-officer.jpg
  - riker-with-duty-officer   # riker-with-duty-officer.jpg
  - riker-five-year-mission-upgrades   # riker-five-year-mission-upgrades.jpg
---

# Riker Automated Command cards

The Bot playing Riker's Crew deck resolves every card with these rows instead of the card's own text (REQ-SOLO-80 to REQ-SOLO-83). Each row becomes one function in `server/engine/bot/riker.py`, following the Bot action rules in CLAUDE.md.

## How a card is resolved

1. If the card has the Surprise trait, resolve its SURPRISE operation and stop (REQ-SOLO-87).
2. Otherwise check the TRAITS rows from top to bottom. The first row with a trait the card has is used. A Wildcard card matches the first trait row (REQ-SOLO-82).
3. If no trait row matches, use the row for the card's suit on whichever SUITS side is face up: WITH NO DUTY OFFICER, or WITH DUTY OFFICER.
4. "Continue resolution" stops the current row and finds the next matching row, trait rows first, then suits (REQ-SOLO-120).
5. A Location still in the Staging Area afterwards moves to the Bot's Control Area (REQ-SOLO-89).

Text shown **in bold** is resolved by the human player. On the card, bold red text is an attack, which the human may cancel; bold black text affects the human without attacking. Rows with an attack list the `ATTACK` action (REQ-SOLO-180 to REQ-SOLO-185).

## Special rule

Cards with any of NX-01, Android, Pakled, Lower Decker, Beverage or Betazoid are considered +1 value for the Bot.

## TRAITS

Image id: `riker-traits`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Surprise | Resolve this card's Surprise operation. | 1. Resolve the card's SURPRISE (Bot only) operation instead of any row. |  | yes |
| 2 | NX-01 / Android / Pakled | Gain 3 [Glory]. Log this card. | 1. Gain 3 [Glory]..<br>2. Log this card. | `GAIN_RESOURCE`, `LOG` | yes |
| 3 | Lower Decker | Gain a Beverage > Cargo. Resolve a Person from the Discard pile, if able; otherwise gain 1 [Research], take an Incident, and resolve the top card of the Supplement deck, then log this card. | 1. Gain a Beverage > Cargo..<br>2. Resolve a Person from the Discard pile, if able; otherwise gain 1 [Research], take an Incident, and resolve the top card of the Supplement deck, then log this card. | `GAIN_CARD`, `RESOLVE_CARD`, `GAIN_SPECIALTY`, `TAKE_INCIDENT`, `LOG` | no |
| 4 | Betazoid | Gain 1 [Influence]. Discard the top card of the Bot deck. Return an Incident from the Bot Discard pile, if able; otherwise send an [Away Team] to a neutral Location. | 1. Gain 1 [Influence]..<br>2. Discard the top card of the Bot deck..<br>3. Return an Incident from the Bot Discard pile, if able; otherwise send an [Away Team] to a neutral Location. | `GAIN_SPECIALTY`, `DISCARD`, `RETURN_INCIDENT`, `SEND_AWAY_TEAM` | yes |
| 5 | Beverage | Gain 1 [Glory], take an Ally and log the Duty Officer. Continue resolution. | 1. Gain 1 [Glory], take an Ally and log the Duty Officer..<br>2. Continue resolution. | `GAIN_RESOURCE`, `GAIN_CARD`, `LOG`, `CONTINUE_RESOLUTION` | no |
| 6 | Attack | Gain 1 [Glory]. **If you have at least 1 Ship at a neutral Location, you either dismiss one of them OR take an Incident.** Continue resolution. | 1. Gain 1 [Glory]..<br>2. If you have at least 1 Ship at a neutral Location, you either dismiss one of them OR take an Incident..<br>3. Continue resolution. | `GAIN_RESOURCE`, `ATTACK`, `DISMISS`, `TAKE_INCIDENT`, `CONTINUE_RESOLUTION` | no |

## SUITS WITH NO DUTY OFFICER

Image id: `riker-no-duty-officer`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Gain a Person. Log the top card of the Bot deck. Gain 1 [Research] / [Military] (whichever is lower). Return this card. | 1. Gain a Person..<br>2. Log the top card of the Bot deck..<br>3. Gain 1 [Research] / [Military] (whichever is lower)..<br>4. Return this card. | `GAIN_CARD`, `LOG`, `GAIN_SPECIALTY`, `RETURN_INCIDENT` | no |
| 2 | Ship | Deploy this Ship; it engages. Discard the top card of the Bot deck. If there is a Starfleet in the Bot discard pile, send an [Away Team] to a neutral Location. | 1. Deploy this Ship; it engages..<br>2. Discard the top card of the Bot deck..<br>3. If there is a Starfleet in the Bot discard pile, send an [Away Team] to a neutral Location. | `DEPLOY`, `ENGAGE`, `DISCARD`, `SEND_AWAY_TEAM` | no |
| 3 | Ally | Take an Incident and a Person. Gain 2 [Research] / [Influence] / [Military] (whichever is lower). Log this card. | 1. Take an Incident and a Person..<br>2. Gain 2 [Research] / [Influence] / [Military] (whichever is lower)..<br>3. Log this card. | `TAKE_INCIDENT`, `GAIN_CARD`, `GAIN_SPECIALTY`, `LOG` | no |
| 4 | Cargo | Junk the most valuable card in the Market (ignoring any with tokens). Gain 1 [Glory]. Resolve a Person / Ally from the Discard pile, if able. Log this card. | 1. Junk the most valuable card in the Market (ignoring any with tokens)..<br>2. Gain 1 [Glory]..<br>3. Resolve a Person / Ally from the Discard pile, if able..<br>4. Log this card. | `JUNK`, `GAIN_RESOURCE`, `RESOLVE_CARD`, `LOG` | no |
| 5 | Person | Discard the top 3 cards of the Bot deck. If one of the discarded cards is Incident, return it; otherwise gain a Cargo. Promote this card to Duty Officer. | 1. Discard the top 3 cards of the Bot deck..<br>2. If one of the discarded cards is Incident, return it; otherwise gain a Cargo..<br>3. Promote this card to Duty Officer. | `DISCARD`, `RETURN_INCIDENT`, `GAIN_CARD`, `PROMOTE` | no |
| 6 | Directive | Gain 1 [Research]. If this card has a Skill icon, gain 2 (additional) [Research]; otherwise take an Incident and a Ship / Ally / Person. Send an [Away Team] to a neutral Location. | 1. Gain 1 [Research]..<br>2. If this card has a Skill icon, gain 2 (additional) [Research]; otherwise take an Incident and a Ship / Ally / Person..<br>3. Send an [Away Team] to a neutral Location. | `GAIN_SPECIALTY`, `TAKE_INCIDENT`, `GAIN_CARD`, `SEND_AWAY_TEAM` | no |
| 7 | Encounter | Discard the entire Bot deck. Gain 2 [Glory]. Log this card. | 1. Discard the entire Bot deck..<br>2. Gain 2 [Glory]..<br>3. Log this card. | `DISCARD`, `GAIN_RESOURCE`, `LOG` | yes |
| 8 | Location | Gain 1 [Influence]. Send an [Away Team] to a neutral Location. | 1. Gain 1 [Influence]..<br>2. Send an [Away Team] to a neutral Location. | `GAIN_SPECIALTY`, `SEND_AWAY_TEAM` | yes |

## SUITS WITH DUTY OFFICER

Image id: `riker-with-duty-officer`.

Used while the Bot has a Duty Officer. Flip back when it is dismissed or logged (REQ-SOLO-91 to REQ-SOLO-95).

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Take a [Research Focus]/[Military Focus], if able. Gain 1 [Research] / [Military] (whichever is higher). Return this card. | 1. Take a [Research Focus]/[Military Focus], if able..<br>2. Gain 1 [Research] / [Military] (whichever is higher)..<br>3. Return this card. | `GAIN_CARD`, `GAIN_SPECIALTY`, `RETURN_INCIDENT` | no |
| 2 | Ship | Deploy this Ship; it engages. Send an [Away Team] to a neutral Location. If this card is Starfleet, resolve a Directive from the Bot Discard pile. Dismiss Duty Officer. | 1. Deploy this Ship; it engages..<br>2. Send an [Away Team] to a neutral Location..<br>3. If this card is Starfleet, resolve a Directive from the Bot Discard pile..<br>4. Dismiss Duty Officer. | `DEPLOY`, `ENGAGE`, `SEND_AWAY_TEAM`, `RESOLVE_CARD`, `DISMISS` | no |
| 3 | Ally | Gain 2 [Influence]. If able to do both, gain [Research Focus]/[Influence Focus]/[Military Focus] and dismiss the Duty Officer. Otherwise log the top card of the Bot deck. Log this card. | 1. Gain 2 [Influence]..<br>2. If able to do both, gain [Research Focus]/[Influence Focus]/[Military Focus] and dismiss the Duty Officer..<br>3. Otherwise log the top card of the Bot deck..<br>4. Log this card. | `GAIN_SPECIALTY`, `GAIN_CARD`, `DISMISS`, `LOG` | no |
| 4 | Cargo | Junk the most valuable card in the Market (ignoring any with tokens). Discard the top 2 cards of the Bot deck. Return an Incident from the Bot Discard pile, if able. Gain 1 [Glory]. | 1. Junk the most valuable card in the Market (ignoring any with tokens)..<br>2. Discard the top 2 cards of the Bot deck..<br>3. Return an Incident from the Bot Discard pile, if able..<br>4. Gain 1 [Glory]. | `JUNK`, `DISCARD`, `RETURN_INCIDENT`, `GAIN_RESOURCE` | no |
| 5 | Person | Take an Incident. Resolve a Ship from the Bot Discard pile if able; otherwise take a Ship and dismiss Duty Officer. | 1. Take an Incident..<br>2. Resolve a Ship from the Bot Discard pile if able; otherwise take a Ship and dismiss Duty Officer. | `TAKE_INCIDENT`, `RESOLVE_CARD`, `GAIN_CARD`, `DISMISS` | no |
| 6 | Directive | If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter, then log this card. Otherwise, gain 1 [Research] / [Military] (whichever is lower), and discard the top 2 cards of the Bot deck. | 1. If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter, then log this card..<br>2. Otherwise, gain 1 [Research] / [Military] (whichever is lower), and discard the top 2 cards of the Bot deck. | `LOG`, `REMOVE_AWAY_TEAM`, `TAKE_ENCOUNTER`, `GAIN_SPECIALTY`, `DISCARD` | no |
| 7 | Encounter | Gain 1 [Glory]. Discard the entire Bot deck. Resolve the top card of the Supplement deck. Return an Incident from the Bot Discard pile, if able. Log this card. | 1. Gain 1 [Glory]..<br>2. Discard the entire Bot deck..<br>3. Resolve the top card of the Supplement deck..<br>4. Return an Incident from the Bot Discard pile, if able..<br>5. Log this card. | `GAIN_RESOURCE`, `DISCARD`, `RESOLVE_CARD`, `RETURN_INCIDENT`, `LOG` | no |
| 8 | Location | Gain 1 [Influence]. Discard the top card of the Supplement deck. Log the Duty Officer. | 1. Gain 1 [Influence]..<br>2. Discard the top card of the Supplement deck..<br>3. Log the Duty Officer. | `GAIN_SPECIALTY`, `DISCARD`, `LOG` | yes |

## Five-Year Mission upgrades

Image id: `riker-five-year-mission-upgrades`. Used only in the solo campaign (REQ-CAMP-25 to REQ-CAMP-31).

### WIN

- **A. Common card types you can reinforce:** Pakled / Lower Decker / Beverage
- **B. Alternative bonuses, pick 1:**
  - BOOST: Before drawing the starting hand, find a Location, except in your Reserve deck, and immediately free play it.
  - BOOST: Before drawing the starting hand, find a Person, except in your Reserve deck, and promote them to Duty Officer.

### LOSS

- **A. Common card types you can reinforce:** [Research] / [Research Focus] / [Military] / [Military Focus]
- **B. Alternative bonuses, pick 1:**
  - BOOST: After drawing the starting hand, choose 2 of the following: find a Ship, except in your Reserve deck OR spend 1 [Latinum] to free play a Ship OR warp a Ship.
  - BOOST: After drawing the starting hand, find a Person, except in your Reserve deck, and promote them to Duty Officer.

## Rulings and open questions

- The WIN reinforce line is printed "BEVERAGE beverage", a misprint for Beverage.
- "Resolve a Person from the Discard pile" on Bot rows means the Bot Discard pile.
- Discarding the entire Bot deck triggers a reshuffle the next time the Bot needs a card (REQ-SOLO-60).

## Tests

- Given the Bot resolves an NX-01 card, it gains 3 Glory and logs the card.
