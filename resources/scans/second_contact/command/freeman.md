---
id: freeman-command
name: Freeman Automated Command cards
suit: Automated Command
deck: freeman
set: second_contact
sides:
  - freeman-traits   # freeman-traits.jpg
  - freeman-no-duty-officer   # freeman-no-duty-officer.jpg
  - freeman-with-duty-officer   # freeman-with-duty-officer.jpg
  - freeman-five-year-mission-upgrades   # freeman-five-year-mission-upgrades.jpg
---

# Freeman Automated Command cards

The Bot playing Freeman's Crew deck resolves every card with these rows instead of the card's own text (REQ-SOLO-80 to REQ-SOLO-83). Each row becomes one function in `server/engine/bot/freeman.py`, following the Bot action rules in CLAUDE.md.

## How a card is resolved

1. If the card has the Surprise trait, resolve its SURPRISE operation and stop (REQ-SOLO-87).
2. Otherwise check the TRAITS rows from top to bottom. The first row with a trait the card has is used. A Wildcard card matches the first trait row (REQ-SOLO-82).
3. If no trait row matches, use the row for the card's suit on whichever SUITS side is face up: WITH NO DUTY OFFICER, or WITH DUTY OFFICER.
4. "Continue resolution" stops the current row and finds the next matching row, trait rows first, then suits (REQ-SOLO-120).
5. A Location still in the Staging Area afterwards moves to the Bot's Control Area (REQ-SOLO-89).

Text shown **in bold** is resolved by the human player. On the card, bold red text is an attack, which the human may cancel; bold black text affects the human without attacking. Rows with an attack list the `ATTACK` action (REQ-SOLO-180 to REQ-SOLO-185).

## Special rule

If a card with Lower Decker would be logged when logging the top card of the Bot deck, discard it instead. Cards with Lower Decker are considered +1 value for the Bot.

## TRAITS

Image id: `freeman-traits`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Surprise | Resolve this card's Surprise operation. | 1. Resolve the card's SURPRISE (Bot only) operation instead of any row. |  | yes |
| 2 | Orion | If the Bot has 3 or fewer [Influence], gain 1 [Influence]. Otherwise, if able gain an Orion including from the Junk; otherwise gain 2 [Glory]. Gain 1 [Influence]. Continue resolution. | 1. If the Bot has 3 or fewer [Influence], gain 1 [Influence]..<br>2. Otherwise, if able gain an Orion including from the Junk; otherwise gain 2 [Glory]..<br>3. Gain 1 [Influence]..<br>4. Continue resolution. | `GAIN_SPECIALTY`, `GAIN_CARD`, `GAIN_RESOURCE`, `CONTINUE_RESOLUTION` | no |
| 3 | Lower Decker | If this card is a Person and the Bot has no Duty Officer, promote this card to Duty Officer and resolve the top card of the Bot deck; otherwise discard the top 2 cards of the Bot deck and continue resolution. | 1. If this card is a Person and the Bot has no Duty Officer, promote this card to Duty Officer and resolve the top card of the Bot deck; otherwise discard the top 2 cards of the Bot deck and continue resolution. | `PROMOTE`, `RESOLVE_CARD`, `DISCARD`, `CONTINUE_RESOLUTION` | no |
| 4 | Anomaly | Junk the most valuable card in the Market (ignoring any with tokens). Gain an Incident and a Cargo. If there is an Anomaly in the Bot's Log already, gain the top Encounter and destroy this card; otherwise log this card. | 1. Junk the most valuable card in the Market (ignoring any with tokens)..<br>2. Gain an Incident and a Cargo..<br>3. If there is an Anomaly in the Bot's Log already, gain the top Encounter and destroy this card; otherwise log this card. | `JUNK`, `TAKE_INCIDENT`, `GAIN_CARD`, `TAKE_ENCOUNTER`, `DESTROY`, `LOG` | no |
| 5 | Doctor | Gain 1 [Research]. Discard the top 2 cards of the Bot deck. If able, return an Incident from the Bot Discard pile; otherwise gain 1 [Research]. | 1. Gain 1 [Research]..<br>2. Discard the top 2 cards of the Bot deck..<br>3. If able, return an Incident from the Bot Discard pile; otherwise gain 1 [Research]. | `GAIN_SPECIALTY`, `DISCARD`, `RETURN_INCIDENT` | yes |
| 6 | Security / Ops | If able, **you remove an [Away Team] from a neutral Location** and the Bot gains 1 [Research] / [Influence] / [Military] (whichever is lower); otherwise gain 2 [Glory] and 2 [Military]. | 1. If able, you remove an [Away Team] from a neutral Location and the Bot gains 1 [Research] / [Influence] / [Military] (whichever is lower); otherwise gain 2 [Glory] and 2 [Military]. | `ATTACK`, `REMOVE_AWAY_TEAM`, `GAIN_SPECIALTY`, `GAIN_RESOURCE` | no |

## SUITS WITH NO DUTY OFFICER

Image id: `freeman-no-duty-officer`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Log the top card of the Bot deck. Return this card. | 1. Log the top card of the Bot deck..<br>2. Return this card. | `LOG`, `RETURN_INCIDENT` | yes |
| 2 | Ship | Deploy this Ship; it explores. Send an [Away Team] to a neutral Location. If able, promote a Person from Bot Discard pile to Duty Officer; otherwise gain a Lower Decker > Orion / Security / Ops > Ally. | 1. Deploy this Ship; it explores..<br>2. Send an [Away Team] to a neutral Location..<br>3. If able, promote a Person from Bot Discard pile to Duty Officer; otherwise gain a Lower Decker > Orion / Security / Ops > Ally. | `DEPLOY`, `EXPLORE`, `SEND_AWAY_TEAM`, `PROMOTE`, `GAIN_CARD` | no |
| 3 | Ally | Gain a Person. Log the top card of the Bot deck. Log this card. | 1. Gain a Person..<br>2. Log the top card of the Bot deck..<br>3. Log this card. | `GAIN_CARD`, `LOG` | no |
| 4 | Cargo | Discard the top 2 cards of the Bot deck. Send an [Away Team] to a neutral Location. If able, promote a Person from Bot Discard pile to Duty Officer; otherwise gain Ship / Ally. | 1. Discard the top 2 cards of the Bot deck..<br>2. Send an [Away Team] to a neutral Location..<br>3. If able, promote a Person from Bot Discard pile to Duty Officer; otherwise gain Ship / Ally. | `DISCARD`, `SEND_AWAY_TEAM`, `PROMOTE`, `GAIN_CARD` | no |
| 5 | Person | Log the top card of the Bot deck. Gain 1 [Research] / [Military] (whichever is lower). If the Bot has 4 or more [Research], gain Lower Decker / Anomaly / Doctor, including from the Junk. If the Bot has 4 or more [Military], send an [Away Team] to a neutral Location. Promote this card to Duty Officer. | 1. Log the top card of the Bot deck..<br>2. Gain 1 [Research] / [Military] (whichever is lower)..<br>3. If the Bot has 4 or more [Research], gain Lower Decker / Anomaly / Doctor, including from the Junk..<br>4. If the Bot has 4 or more [Military], send an [Away Team] to a neutral Location..<br>5. Promote this card to Duty Officer. | `LOG`, `GAIN_SPECIALTY`, `GAIN_CARD`, `SEND_AWAY_TEAM`, `PROMOTE` | no |
| 6 | Directive | Take a Lower Decker if able; otherwise gain a Ship / Ally and take an Incident. Send an [Away Team] to a neutral Location. | 1. Take a Lower Decker if able; otherwise gain a Ship / Ally and take an Incident..<br>2. Send an [Away Team] to a neutral Location. | `GAIN_CARD`, `TAKE_INCIDENT`, `SEND_AWAY_TEAM` | no |
| 7 | Encounter | Gain 2 [Glory] and log this card. | 1. Gain 2 [Glory] and log this card. | `GAIN_RESOURCE`, `LOG` | yes |
| 8 | Location | Gain 1 [Influence]. Discard the top card of the Bot deck. Return an Incident from the Bot Discard pile if able; otherwise gain a Person. | 1. Gain 1 [Influence]..<br>2. Discard the top card of the Bot deck..<br>3. Return an Incident from the Bot Discard pile if able; otherwise gain a Person. | `GAIN_SPECIALTY`, `DISCARD`, `RETURN_INCIDENT`, `GAIN_CARD` | no |

## SUITS WITH DUTY OFFICER

Image id: `freeman-with-duty-officer`.

Used while the Bot has a Duty Officer. Flip back when it is dismissed or logged (REQ-SOLO-91 to REQ-SOLO-95).

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Send an [Away Team] to a neutral Location. Gain 1 [Military]. Return this card. | 1. Send an [Away Team] to a neutral Location..<br>2. Gain 1 [Military]..<br>3. Return this card. | `SEND_AWAY_TEAM`, `GAIN_SPECIALTY`, `RETURN_INCIDENT` | yes |
| 2 | Ship | Deploy this Ship; it explores. Send an [Away Team] to a neutral Location. If Duty Officer is Lower Decker, dismiss them; otherwise log them and the top card of the Bot deck. | 1. Deploy this Ship; it explores..<br>2. Send an [Away Team] to a neutral Location..<br>3. If Duty Officer is Lower Decker, dismiss them; otherwise log them and the top card of the Bot deck. | `DEPLOY`, `EXPLORE`, `SEND_AWAY_TEAM`, `DISMISS`, `LOG` | no |
| 3 | Ally | Discard the top 2 cards of the Bot deck. Gain a Person. Log the top card of the Bot deck. Log this card. | 1. Discard the top 2 cards of the Bot deck..<br>2. Gain a Person..<br>3. Log the top card of the Bot deck..<br>4. Log this card. | `DISCARD`, `GAIN_CARD`, `LOG` | no |
| 4 | Cargo | Discard the top 2 cards of the Bot deck. Gain a Person. If able, resolve a Ship from the Bot Discard pile; otherwise gain 1 [Research]/[Influence]/[Military], whichever is higher. Log the top card of the Bot deck. Log this card. | 1. Discard the top 2 cards of the Bot deck..<br>2. Gain a Person..<br>3. If able, resolve a Ship from the Bot Discard pile; otherwise gain 1 [Research]/[Influence]/[Military], whichever is higher..<br>4. Log the top card of the Bot deck..<br>5. Log this card. | `DISCARD`, `GAIN_CARD`, `RESOLVE_CARD`, `GAIN_SPECIALTY`, `LOG` | no |
| 5 | Person | Gain 1 [Research]. If this card is Synthetic take an Incident and discard the top card of the Supplement deck. If able, gain a [Research Focus]/[Influence Focus]/[Military Focus] > Ship. Dismiss Duty Officer. | 1. Gain 1 [Research]..<br>2. If this card is Synthetic take an Incident and discard the top card of the Supplement deck..<br>3. If able, gain a [Research Focus]/[Influence Focus]/[Military Focus] > Ship..<br>4. Dismiss Duty Officer. | `GAIN_SPECIALTY`, `TAKE_INCIDENT`, `DISCARD`, `GAIN_CARD`, `DISMISS` | no |
| 6 | Directive | If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter, then log this card. Otherwise gain 1 [Research] / [Military], whichever is lower, and discard the top card of the Bot deck. | 1. If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter, then log this card..<br>2. Otherwise gain 1 [Research] / [Military], whichever is lower, and discard the top card of the Bot deck. | `LOG`, `REMOVE_AWAY_TEAM`, `TAKE_ENCOUNTER`, `GAIN_SPECIALTY`, `DISCARD` | no |
| 7 | Encounter | Take a Lower Decker / Orion / Anomaly / Doctor / Security / Ops, if able, and log this card; otherwise log the top 2 cards of the Bot deck. | 1. Take a Lower Decker / Orion / Anomaly / Doctor / Security / Ops, if able, and log this card; otherwise log the top 2 cards of the Bot deck. | `GAIN_CARD`, `LOG` | no |
| 8 | Location | Discard the top 2 cards of the Bot deck. Gain 1 [Influence]. Log the top card of the Bot deck. If the Duty Officer is Lower Decker, dismiss them; otherwise log them. | 1. Discard the top 2 cards of the Bot deck..<br>2. Gain 1 [Influence]..<br>3. Log the top card of the Bot deck..<br>4. If the Duty Officer is Lower Decker, dismiss them; otherwise log them. | `DISCARD`, `GAIN_SPECIALTY`, `LOG`, `DISMISS` | yes |

## Five-Year Mission upgrades

Image id: `freeman-five-year-mission-upgrades`. Used only in the solo campaign (REQ-CAMP-25 to REQ-CAMP-31).

### WIN

- **A. Common card types you can reinforce:** Lower Decker / Anomaly / Starfleet
- **B. Alternative bonuses, pick 1:**
  - BOOST: Before drawing the starting hand, take an Incident to scan for Lower Decker.
  - BOOST: After drawing the starting hand, find an Incident and return it.

### LOSS

- **A. Common card types you can reinforce:** Ally / Starfleet
- **B. Alternative bonuses, pick 1:**
  - REINFORCE: A Person from your Available cards or Reserve deck.
  - BOOST: Gain an [Action].

## Rulings and open questions

- A Fleet of 30 California-Class Ships counts as 2 tokens for securing when played by the Bot too (REQ-EXP-FRE-02).

## Tests

- Given the Bot logs the top card of the Bot deck and it is a Lower Decker, the card is discarded instead.
