---
id: kirk-command
name: Kirk Automated Command cards
suit: Automated Command
deck: kirk
set: to_boldly_go
sides:
  - kirk-traits   # kirk-traits.jpg
  - kirk-no-duty-officer   # kirk-no-duty-officer.jpg
  - kirk-with-duty-officer   # kirk-with-duty-officer.jpg
  - kirk-five-year-mission-upgrades   # kirk-five-year-mission-upgrades.jpg
---

# Kirk Automated Command cards

The Bot playing Kirk's Crew deck resolves every card with these rows instead of the card's own text (REQ-SOLO-80 to REQ-SOLO-83). Each row becomes one function in `server/engine/bot/kirk.py`, following the Bot action rules in CLAUDE.md.

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

Image id: `kirk-traits`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Surprise | Resolve this card's Surprise operation. | 1. Resolve the card's SURPRISE (Bot only) operation instead of any row. |  | yes |
| 2 | Time Travel | Gain 2 [Research] / [Influence] / [Military] (whichever is lower). Resolve the top card of the Bot deck. Log this card. | 1. Gain 2 [Research] / [Influence] / [Military] (whichever is lower)..<br>2. Resolve the top card of the Bot deck..<br>3. Log this card. | `GAIN_SPECIALTY`, `RESOLVE_CARD`, `LOG` | no |
| 3 | Klingon | Gain 1 [Military]. If this card is a Ship, deploy it; it engages. If this card is a Person, promote it to Duty Officer. If able, resolve a Directive from Bot Discard pile. Otherwise, send an [Away Team] to a neutral Location. | 1. Gain 1 [Military]..<br>2. If this card is a Ship, deploy it; it engages..<br>3. If this card is a Person, promote it to Duty Officer..<br>4. If able, resolve a Directive from Bot Discard pile..<br>5. Otherwise, send an [Away Team] to a neutral Location. | `GAIN_SPECIALTY`, `DEPLOY`, `ENGAGE`, `PROMOTE`, `RESOLVE_CARD`, `SEND_AWAY_TEAM` | no |
| 4 | Attack | If able, log a deployed Ship to send 2 [Away Team] to a neutral Location and **you discard a card**. Otherwise, discard the top 2 cards of the Bot deck and **you dismiss a Duty Officer and take an Incident**. If this card is a Person, promote it to Duty Officer. | 1. If able, log a deployed Ship to send 2 [Away Team] to a neutral Location and you discard a card..<br>2. Otherwise, discard the top 2 cards of the Bot deck and you dismiss a Duty Officer and take an Incident..<br>3. If this card is a Person, promote it to Duty Officer. | `LOG`, `SEND_AWAY_TEAM`, `ATTACK`, `DISCARD`, `DISMISS`, `TAKE_INCIDENT`, `PROMOTE` | no |
| 5 | Engineer | Discard the top 2 cards of the Bot deck. If able, resolve a Ship in Bot Discard pile. Otherwise, discard the top card of the Supplement deck. If this card is a Person, promote it to Duty Officer. | 1. Discard the top 2 cards of the Bot deck..<br>2. If able, resolve a Ship in Bot Discard pile..<br>3. Otherwise, discard the top card of the Supplement deck..<br>4. If this card is a Person, promote it to Duty Officer. | `DISCARD`, `RESOLVE_CARD`, `PROMOTE` | no |
| 6 | Scientist / Vulcan | Log the top card of the Bot deck. Gain 1 [Research] / [Influence] / [Military] (whichever is lower). Gain 1 [Research] / [Influence] / [Military] (whichever is lower). If this card is a Person and the Bot has no Duty Officer, promote it to Duty Officer. Otherwise, send an [Away Team] to a neutral Location. | 1. Log the top card of the Bot deck..<br>2. Gain 1 [Research] / [Influence] / [Military] (whichever is lower)..<br>3. Gain 1 [Research] / [Influence] / [Military] (whichever is lower)..<br>4. If this card is a Person and the Bot has no Duty Officer, promote it to Duty Officer..<br>5. Otherwise, send an [Away Team] to a neutral Location. | `LOG`, `GAIN_SPECIALTY`, `PROMOTE`, `SEND_AWAY_TEAM` | yes |

## SUITS WITH NO DUTY OFFICER

Image id: `kirk-no-duty-officer`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Log the top card of the Bot deck. Gain a Person. Return this card. | 1. Log the top card of the Bot deck..<br>2. Gain a Person..<br>3. Return this card. | `LOG`, `GAIN_CARD`, `RETURN_INCIDENT` | no |
| 2 | Ship | Deploy this Ship; it explores. If Bot has 5+ [Influence], send an [Away Team] to a neutral Location, ignoring any opponent Ship. Otherwise, gain 1 [Influence]. | 1. Deploy this Ship; it explores..<br>2. If Bot has 5+ [Influence], send an [Away Team] to a neutral Location, ignoring any opponent Ship..<br>3. Otherwise, gain 1 [Influence]. | `DEPLOY`, `EXPLORE`, `SEND_AWAY_TEAM`, `GAIN_SPECIALTY` | no |
| 3 | Ally | Discard the top 2 cards of the Bot deck. Gain 1 [Research] / [Influence] / [Military] (whichever is lower). If Bot has 5+ [Influence], gain 2 [Glory] and log this card. | 1. Discard the top 2 cards of the Bot deck..<br>2. Gain 1 [Research] / [Influence] / [Military] (whichever is lower)..<br>3. If Bot has 5+ [Influence], gain 2 [Glory] and log this card. | `DISCARD`, `GAIN_SPECIALTY`, `GAIN_RESOURCE`, `LOG` | yes |
| 4 | Cargo | Discard the top 2 cards of the Bot deck. If able, promote a Person from Bot Discard pile to Duty Officer. Otherwise, gain a Vulcan > Person and log this card. | 1. Discard the top 2 cards of the Bot deck..<br>2. If able, promote a Person from Bot Discard pile to Duty Officer..<br>3. Otherwise, gain a Vulcan > Person and log this card. | `DISCARD`, `PROMOTE`, `GAIN_CARD`, `LOG` | no |
| 5 | Person | Gain 1 [Research] / [Influence] / [Military] (whichever is lower). Send an [Away Team] to a neutral Location. Promote this card to Duty Officer. | 1. Gain 1 [Research] / [Influence] / [Military] (whichever is lower)..<br>2. Send an [Away Team] to a neutral Location..<br>3. Promote this card to Duty Officer. | `GAIN_SPECIALTY`, `SEND_AWAY_TEAM`, `PROMOTE` | yes |
| 6 | Directive | Gain a Ship / Ally and take an Incident. Send an [Away Team] to a neutral Location. | 1. Gain a Ship / Ally and take an Incident..<br>2. Send an [Away Team] to a neutral Location. | `GAIN_CARD`, `TAKE_INCIDENT`, `SEND_AWAY_TEAM` | no |
| 7 | Encounter | Log the top card of the Bot deck. Gain the card in the Market with the most [Glory]. | 1. Log the top card of the Bot deck..<br>2. Gain the card in the Market with the most [Glory]. | `LOG`, `GAIN_CARD` | no |
| 8 | Location | Log the top card of the Bot deck. Gain 1 [Research] / [Influence] / [Military] (whichever is lower). Send an [Away Team] to a neutral Location. | 1. Log the top card of the Bot deck..<br>2. Gain 1 [Research] / [Influence] / [Military] (whichever is lower)..<br>3. Send an [Away Team] to a neutral Location. | `LOG`, `GAIN_SPECIALTY`, `SEND_AWAY_TEAM` | yes |

## SUITS WITH DUTY OFFICER

Image id: `kirk-with-duty-officer`.

Used while the Bot has a Duty Officer. Flip back when it is dismissed or logged (REQ-SOLO-91 to REQ-SOLO-95).

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Discard the top card of the Bot deck. Gain 1 [Research] / [Influence] / [Military] (whichever is lower). Log Duty Officer. Return this card. | 1. Discard the top card of the Bot deck..<br>2. Gain 1 [Research] / [Influence] / [Military] (whichever is lower)..<br>3. Log Duty Officer..<br>4. Return this card. | `DISCARD`, `GAIN_SPECIALTY`, `LOG`, `RETURN_INCIDENT` | yes |
| 2 | Ship | Gain 1 [Military]. Deploy this Ship; it engages. Send an [Away Team] to a neutral Location. | 1. Gain 1 [Military]..<br>2. Deploy this Ship; it engages..<br>3. Send an [Away Team] to a neutral Location. | `GAIN_SPECIALTY`, `DEPLOY`, `ENGAGE`, `SEND_AWAY_TEAM` | no |
| 3 | Ally | Discard the top card of the Bot deck. Gain 1 [Research]. Gain Any Species excluding Human > Person / Ally. Log Duty Officer. Log this card. | 1. Discard the top card of the Bot deck..<br>2. Gain 1 [Research]..<br>3. Gain Any Species excluding Human > Person / Ally..<br>4. Log Duty Officer..<br>5. Log this card. | `DISCARD`, `GAIN_SPECIALTY`, `GAIN_CARD`, `LOG` | no |
| 4 | Cargo | Log the top card of the Bot deck. Gain 1 [Research]. Gain a Ship. Deploy the gained Ship; it explores. | 1. Log the top card of the Bot deck..<br>2. Gain 1 [Research]..<br>3. Gain a Ship..<br>4. Deploy the gained Ship; it explores. | `LOG`, `GAIN_SPECIALTY`, `GAIN_CARD`, `DEPLOY`, `EXPLORE` | no |
| 5 | Person | Discard the top card of the Bot deck. Gain a Vulcan > Any Species excluding Human > Person / Cargo / Ship / Ally. | 1. Discard the top card of the Bot deck..<br>2. Gain a Vulcan > Any Species excluding Human > Person / Cargo / Ship / Ally. | `DISCARD`, `GAIN_CARD` | no |
| 6 | Directive | If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter, then log this card. Otherwise, discard the top card of the Supplement deck. | 1. If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter, then log this card..<br>2. Otherwise, discard the top card of the Supplement deck. | `LOG`, `REMOVE_AWAY_TEAM`, `TAKE_ENCOUNTER`, `DISCARD` | no |
| 7 | Encounter | Gain 1 [Research]. Gain 1 [Influence]. Gain 1 [Military]. Gain 1 [Glory]. Log this card. | 1. Gain 1 [Research]..<br>2. Gain 1 [Influence]..<br>3. Gain 1 [Military]..<br>4. Gain 1 [Glory]..<br>5. Log this card. | `GAIN_SPECIALTY`, `GAIN_RESOURCE`, `LOG` | yes |
| 8 | Location | Gain 1 [Research]. Gain 1 [Influence]. Gain 1 [Military]. Take an Incident. If able, deploy a Ship from Bot Discard pile; it explores. Otherwise, send an [Away Team] to neutral Location. Log Duty Officer. | 1. Gain 1 [Research]..<br>2. Gain 1 [Influence]..<br>3. Gain 1 [Military]..<br>4. Take an Incident..<br>5. If able, deploy a Ship from Bot Discard pile; it explores..<br>6. Otherwise, send an [Away Team] to neutral Location..<br>7. Log Duty Officer. | `GAIN_SPECIALTY`, `TAKE_INCIDENT`, `DEPLOY`, `EXPLORE`, `SEND_AWAY_TEAM`, `LOG` | no |

## Five-Year Mission upgrades

Image id: `kirk-five-year-mission-upgrades`. Used only in the solo campaign (REQ-CAMP-25 to REQ-CAMP-31).

### WIN

- **A. Common card types you can reinforce:** Person
- **B. Alternative bonuses, pick 1:**
  - BOOST: Before drawing the starting hand, discard the top card of your deck and gain 2 [Research]/[Influence]/[Military].
  - BOOST: Send an [Away Team] each to two different neutral Location.

### LOSS

- **A. Common card types you can reinforce:** Vulcan / Time Travel / Klingon
- **B. Alternative bonuses, pick 1:**
  - BOOST: Gain 1 [Research]/[Influence]/[Military].
  - BOOST: After drawing the starting hand, find a Directive in your Draw deck.

## Rulings and open questions

- The solo rulebook's example of upgrade cards (p. 16) describes Kirk's card; the scan shows the current printed options.

## Tests

- Given the Bot has 5 Influence, when it resolves a Ship with no Duty Officer, it deploys, explores, and sends an Away Team ignoring the human's Ships.
