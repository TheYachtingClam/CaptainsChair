---
id: koloth-command
name: Koloth Automated Command cards
suit: Automated Command
deck: koloth
set: base_game
sides:
  - koloth-traits   # koloth-traits.jpg
  - koloth-no-duty-officer   # koloth-no-duty-officer.jpg
  - koloth-with-duty-officer   # koloth-with-duty-officer.jpg
  - koloth-five-year-mission-upgrades   # koloth-five-year-mission-upgrades.jpg
---

# Koloth Automated Command cards

The Bot playing Koloth's Crew deck resolves every card with these rows instead of the card's own text (REQ-SOLO-80 to REQ-SOLO-83). Each row becomes one function in `server/engine/bot/koloth.py`, following the Bot action rules in CLAUDE.md.

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

Image id: `koloth-traits`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Surprise | Resolve this card's Surprise operation. | 1. Resolve the card's SURPRISE (Bot only) operation instead of any row. |  | yes |
| 2 | Weapon | Junk the most valuable card in the Market (ignoring any with tokens). Gain 1 [Military]. If Bot has 9+ [Military] and Bot Duty Officer is a Klingon, dismiss Duty Officer, gain 4 [Glory], and log this card. Otherwise, **if able, you remove [Away Team].** Otherwise, gain 1 [Military]. | 1. Junk the most valuable card in the Market (ignoring any with tokens).<br>2. Gain 1 [Military].<br>3. If Bot has 9+ [Military] and Bot Duty Officer is a Klingon, dismiss Duty Officer, gain 4 [Glory], and log this card.<br>4. Otherwise, if able, you remove [Away Team].<br>5. Otherwise, gain 1 [Military]. | `JUNK`, `GAIN_SPECIALTY`, `DISMISS`, `GAIN_RESOURCE`, `LOG`, `ATTACK`, `REMOVE_AWAY_TEAM` | no |
| 3 | Attack | Junk the most valuable card in the Market (ignoring any with tokens). If able, return a Ship from discard to the top of the Bot deck. Otherwise, **if able, you dismiss Ship.** Otherwise gain 1 [Glory]. | 1. Junk the most valuable card in the Market (ignoring any with tokens).<br>2. If able, return a Ship from discard to the top of the Bot deck.<br>3. Otherwise, if able, you dismiss Ship.<br>4. Otherwise gain 1 [Glory]. | `JUNK`, `PUT`, `ATTACK`, `DISMISS`, `GAIN_RESOURCE` | no |
| 4 | Romulan | Log the top card of the Bot deck. Take the top card of the Supplement deck. Log this card. | 1. Log the top card of the Bot deck.<br>2. Take the top card of the Supplement deck.<br>3. Log this card. | `LOG`, `PUT` | yes |
| 5 | Scientist | Discard the top card of the Bot deck. Gain 2 [Glory]. Gain 1 [Influence]. | 1. Discard the top card of the Bot deck.<br>2. Gain 2 [Glory].<br>3. Gain 1 [Influence]. | `DISCARD`, `GAIN_RESOURCE`, `GAIN_SPECIALTY` | yes |

## SUITS WITH NO DUTY OFFICER

Image id: `koloth-no-duty-officer`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Gain a [Military Focus] > Person / Ship. Send an [Away Team] to a neutral Location. **You may draw a card.** Return this card. | 1. Gain a [Military Focus] > Person / Ship.<br>2. Send an [Away Team] to a neutral Location.<br>3. You may draw a card.<br>4. Return this card. | `GAIN_CARD`, `SEND_AWAY_TEAM`, `DRAW`, `RETURN_INCIDENT` | no |
| 2 | Ship | Deploy this Ship; it explores. Send an [Away Team] to a neutral Location. | 1. Deploy this Ship; it explores.<br>2. Send an [Away Team] to a neutral Location. | `DEPLOY`, `EXPLORE`, `SEND_AWAY_TEAM` | yes |
| 3 | Ally | If able, gain a Romulan. Otherwise, take a Ship / Person and **you take an Incident.** Log this card. | 1. If able, gain a Romulan.<br>2. Otherwise, take a Ship / Person and you take an Incident.<br>3. Log this card. | `GAIN_CARD`, `ATTACK`, `TAKE_INCIDENT`, `LOG` | no |
| 4 | Cargo | Gain 1 [Influence]. Gain 1 [Military]. Gain a Person / Ship / Ally. | 1. Gain 1 [Influence].<br>2. Gain 1 [Military].<br>3. Gain a Person / Ship / Ally. | `GAIN_SPECIALTY`, `GAIN_CARD` | no |
| 5 | Person | Discard the top card of the Bot deck. Log the top card of the Bot deck. Gain 1 [Military] / [Influence] (whichever is lower). Gain a Weapon > Ship. Promote this card to Duty Officer. | 1. Discard the top card of the Bot deck.<br>2. Log the top card of the Bot deck.<br>3. Gain 1 [Military] / [Influence] (whichever is lower).<br>4. Gain a Weapon > Ship.<br>5. Promote this card to Duty Officer. | `DISCARD`, `LOG`, `GAIN_SPECIALTY`, `GAIN_CARD`, `PROMOTE` | no |
| 6 | Directive | Discard the top 3 cards of the Bot deck. Gain 1 [Military]. Take an Incident. Send an [Away Team] to a neutral Location. | 1. Discard the top 3 cards of the Bot deck.<br>2. Gain 1 [Military].<br>3. Take an Incident.<br>4. Send an [Away Team] to a neutral Location. | `DISCARD`, `GAIN_SPECIALTY`, `TAKE_INCIDENT`, `SEND_AWAY_TEAM` | no |
| 7 | Encounter | Gain a Person / Ally. Send an [Away Team] to a neutral Location. Log this card. | 1. Gain a Person / Ally.<br>2. Send an [Away Team] to a neutral Location.<br>3. Log this card. | `GAIN_CARD`, `SEND_AWAY_TEAM`, `LOG` | no |
| 8 | Location | Log the top card of the Bot deck. Discard the top 2 cards of the Bot deck. If a Ship is in Bot Discard pile, gain 1 [Glory]. | 1. Log the top card of the Bot deck.<br>2. Discard the top 2 cards of the Bot deck.<br>3. If a Ship is in Bot Discard pile, gain 1 [Glory]. | `LOG`, `DISCARD`, `GAIN_RESOURCE` | yes |

## SUITS WITH DUTY OFFICER

Image id: `koloth-with-duty-officer`.

Used while the Bot has a Duty Officer. Flip back when it is dismissed or logged (REQ-SOLO-91 to REQ-SOLO-95).

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Gain 1 [Military]. If able, gain a Romulan. Otherwise, take a [Military Focus] > Cargo. Send an [Away Team] to a neutral Location. Return this card. | 1. Gain 1 [Military].<br>2. If able, gain a Romulan.<br>3. Otherwise, take a [Military Focus] > Cargo.<br>4. Send an [Away Team] to a neutral Location.<br>5. Return this card. | `GAIN_SPECIALTY`, `GAIN_CARD`, `SEND_AWAY_TEAM`, `RETURN_INCIDENT` | no |
| 2 | Ship | Gain 1 [Influence]. Deploy this Ship; it engages. Send an [Away Team] to a neutral Location. | 1. Gain 1 [Influence].<br>2. Deploy this Ship; it engages.<br>3. Send an [Away Team] to a neutral Location. | `GAIN_SPECIALTY`, `DEPLOY`, `ENGAGE`, `SEND_AWAY_TEAM` | yes |
| 3 | Ally | If able, gain a Romulan. Otherwise, take an Incident, gain 1 [Glory], **you take an Incident and discard it**, then dismiss Duty Officer. Log this card. | 1. If able, gain a Romulan.<br>2. Otherwise, take an Incident, gain 1 [Glory], you take an Incident and discard it, then dismiss Duty Officer.<br>3. Log this card. | `GAIN_CARD`, `TAKE_INCIDENT`, `GAIN_RESOURCE`, `ATTACK`, `DISCARD`, `DISMISS`, `LOG` | no |
| 4 | Cargo | Gain 1 [Influence]. Gain 1 [Military]. Discard the top card of the Supplement deck. Log Duty Officer. | 1. Gain 1 [Influence].<br>2. Gain 1 [Military].<br>3. Discard the top card of the Supplement deck.<br>4. Log Duty Officer. | `GAIN_SPECIALTY`, `DISCARD`, `LOG` | yes |
| 5 | Person | Log the top card of Bot deck. Gain a Cargo. If able, return a Ship from Bot Discard pile to the top of the Bot deck. Otherwise, take a Ship. | 1. Log the top card of Bot deck.<br>2. Gain a Cargo.<br>3. If able, return a Ship from Bot Discard pile to the top of the Bot deck.<br>4. Otherwise, take a Ship. | `LOG`, `GAIN_CARD`, `PUT` | no |
| 6 | Directive | If able to do both, log a Ship and remove an [Away Team] to take top Encounter, then log this card and log Duty Officer. Otherwise, gain 1 [Glory], 1 [Military], and a Person. | 1. If able to do both, log a Ship and remove an [Away Team] to take top Encounter, then log this card and log Duty Officer.<br>2. Otherwise, gain 1 [Glory], 1 [Military], and a Person. | `LOG`, `REMOVE_AWAY_TEAM`, `TAKE_ENCOUNTER`, `GAIN_RESOURCE`, `GAIN_SPECIALTY`, `GAIN_CARD` | no |
| 7 | Encounter | Gain 1 [Influence] / [Military] (whichever is higher). Gain a Ship. Deploy the gained Ship; it engages. | 1. Gain 1 [Influence] / [Military] (whichever is higher).<br>2. Gain a Ship.<br>3. Deploy the gained Ship; it engages. | `GAIN_SPECIALTY`, `GAIN_CARD`, `DEPLOY`, `ENGAGE` | no |
| 8 | Location | Dismiss Duty Officer. Gain 1 [Glory]. Resolve the top card of the Bot deck. | 1. Dismiss Duty Officer.<br>2. Gain 1 [Glory].<br>3. Resolve the top card of the Bot deck. | `DISMISS`, `GAIN_RESOURCE`, `RESOLVE_CARD` | no |

## Five-Year Mission upgrades

Image id: `koloth-five-year-mission-upgrades`. Used only in the solo campaign (REQ-CAMP-25 to REQ-CAMP-31).

### WIN

- **A. Common card types you can reinforce:** Ship
- **B. Alternative bonuses, pick 1:**
  - BOOST: Gain 3 [Military].
  - BOOST: Gain 2 [Glory].

### LOSS

- **A. Common card types you can reinforce:** Weapon / Attack / Klingon
- **B. Alternative bonuses, pick 1:**
  - REINFORCE: A non-Incident card from your Reserve deck
  - REINFORCE: A non-Incident card from your Available cards.

## Rulings and open questions

- Weapon and Attack rows: the human chooses which Away Team to remove and which Ship to dismiss (REQ-SOLO-183).
- 'Take the top card of the Supplement deck' puts it on top of the Bot deck.
- Incident row with no Duty Officer: 'You may draw a card' is bold black, a benefit for the human, not an attack.
- "If able to do both, log ... and remove ... to take top Encounter" rows follow the same reading as the other Bots' Directive rows.

## Tests

- Given a card with a trait on the TRAITS side, when the Bot resolves it, then the first matching trait row is used.
- Given a card with no matching trait, when the Bot resolves it, then the row for its suit on the SUITS side face up is used.
