---
id: shran-command
name: Shran Automated Command cards
suit: Automated Command
deck: shran
set: base_game
sides:
  - shran-traits   # shran-traits.jpg
  - shran-no-duty-officer   # shran-no-duty-officer.jpg
  - shran-with-duty-officer   # shran-with-duty-officer.jpg
  - shran-five-year-mission-upgrades   # shran-five-year-mission-upgrades.jpg
---

# Shran Automated Command cards

The Bot playing Shran's Crew deck resolves every card with these rows instead of the card's own text (REQ-SOLO-80 to REQ-SOLO-83). Each row becomes one function in `server/engine/bot/shran.py`, following the Bot action rules in CLAUDE.md.

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

Image id: `shran-traits`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Surprise | Resolve this card's Surprise operation. | 1. Resolve the card's SURPRISE (Bot only) operation instead of any row. |  | yes |
| 2 | Weapon | Junk the most valuable card in the Market (ignoring any with tokens). Send an [Away Team] to a neutral Location. Either **you take an Incident OR you remove an [Away Team].** | 1. Junk the most valuable card in the Market (ignoring any with tokens).<br>2. Send an [Away Team] to a neutral Location.<br>3. Either you take an Incident OR you remove an [Away Team]. | `JUNK`, `SEND_AWAY_TEAM`, `ATTACK`, `TAKE_INCIDENT`, `REMOVE_AWAY_TEAM` | no |
| 3 | Attack | Send an [Away Team] to a neutral Location. **You discard the top card of your deck.** If it is a Person, **you take an Incident** and the Bot takes an Incident. Otherwise, gain 1 [Military]. If this card is a Person, promote it to Duty Officer. | 1. Send an [Away Team] to a neutral Location.<br>2. You discard the top card of your deck.<br>3. If it is a Person, you take an Incident and the Bot takes an Incident.<br>4. Otherwise, gain 1 [Military].<br>5. If this card is a Person, promote it to Duty Officer. | `SEND_AWAY_TEAM`, `ATTACK`, `DISCARD`, `TAKE_INCIDENT`, `GAIN_SPECIALTY`, `PROMOTE` | no |
| 4 | Business | Log the top card of the Bot deck. Gain a Weapon > Cargo / Ship. Resolve the top card of the Bot deck. Log this card. | 1. Log the top card of the Bot deck.<br>2. Gain a Weapon > Cargo / Ship.<br>3. Resolve the top card of the Bot deck.<br>4. Log this card. | `LOG`, `GAIN_CARD`, `RESOLVE_CARD` | no |
| 5 | Ambassador | Discard the top 2 cards of the Bot deck. Gain 2 [Glory]. **You may return an Incident from your hand or discard pile.** If this card is a Person, promote it to Duty Officer. Otherwise, log this card. | 1. Discard the top 2 cards of the Bot deck.<br>2. Gain 2 [Glory].<br>3. You may return an Incident from your hand or discard pile.<br>4. If this card is a Person, promote it to Duty Officer.<br>5. Otherwise, log this card. | `DISCARD`, `GAIN_RESOURCE`, `RETURN_INCIDENT`, `PROMOTE`, `LOG` | yes |

## SUITS WITH NO DUTY OFFICER

Image id: `shran-no-duty-officer`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Gain a Person. Discard the top 3 cards of the Bot deck. Return this card. | 1. Gain a Person.<br>2. Discard the top 3 cards of the Bot deck.<br>3. Return this card. | `GAIN_CARD`, `DISCARD`, `RETURN_INCIDENT` | no |
| 2 | Ship | Deploy this Ship; it explores. If a Person is in Bot Discard pile, send an [Away Team] to a neutral Location. If a Cargo is in Bot Discard pile, gain 1 [Influence]. | 1. Deploy this Ship; it explores.<br>2. If a Person is in Bot Discard pile, send an [Away Team] to a neutral Location.<br>3. If a Cargo is in Bot Discard pile, gain 1 [Influence]. | `DEPLOY`, `EXPLORE`, `SEND_AWAY_TEAM`, `GAIN_SPECIALTY` | yes |
| 3 | Ally | Discard the top 3 cards of the Bot deck. For each Person in Bot Discard pile, gain 1 [Influence]. For each Ship in Bot Discard pile, send an [Away Team] to a neutral Location. | 1. Discard the top 3 cards of the Bot deck.<br>2. For each Person in Bot Discard pile, gain 1 [Influence].<br>3. For each Ship in Bot Discard pile, send an [Away Team] to a neutral Location. | `DISCARD`, `GAIN_SPECIALTY`, `SEND_AWAY_TEAM` | yes |
| 4 | Cargo | Discard the top 2 cards of the Bot deck. Gain 2 [Glory]. Gain a Business > Person. Log this card. | 1. Discard the top 2 cards of the Bot deck.<br>2. Gain 2 [Glory].<br>3. Gain a Business > Person.<br>4. Log this card. | `DISCARD`, `GAIN_RESOURCE`, `GAIN_CARD`, `LOG` | no |
| 5 | Person | Discard the top 2 cards of the Bot deck. Gain 1 [Influence] / [Military] (whichever is lower). Send an [Away Team] to a neutral Location. Promote this card to Duty Officer. | 1. Discard the top 2 cards of the Bot deck.<br>2. Gain 1 [Influence] / [Military] (whichever is lower).<br>3. Send an [Away Team] to a neutral Location.<br>4. Promote this card to Duty Officer. | `DISCARD`, `GAIN_SPECIALTY`, `SEND_AWAY_TEAM`, `PROMOTE` | yes |
| 6 | Directive | Gain a Business > Cargo. Send an [Away Team] to a neutral Location. If Bot has 5+ [Influence], gain 1 [Glory] and take an Incident. | 1. Gain a Business > Cargo.<br>2. Send an [Away Team] to a neutral Location.<br>3. If Bot has 5+ [Influence], gain 1 [Glory] and take an Incident. | `GAIN_CARD`, `SEND_AWAY_TEAM`, `GAIN_RESOURCE`, `TAKE_INCIDENT` | no |
| 7 | Encounter | Discard the top 2 cards of the Bot deck. Gain a Person. Gain a Cargo. Log this card. | 1. Discard the top 2 cards of the Bot deck.<br>2. Gain a Person.<br>3. Gain a Cargo.<br>4. Log this card. | `DISCARD`, `GAIN_CARD`, `LOG` | no |
| 8 | Location | Log the top card of the Bot deck. Discard the top 2 cards of the Bot deck. | 1. Log the top card of the Bot deck.<br>2. Discard the top 2 cards of the Bot deck. | `LOG`, `DISCARD` | yes |

## SUITS WITH DUTY OFFICER

Image id: `shran-with-duty-officer`.

Used while the Bot has a Duty Officer. Flip back when it is dismissed or logged (REQ-SOLO-91 to REQ-SOLO-95).

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Log the top card of the Bot deck. Gain 1 [Glory]. Return this card. | 1. Log the top card of the Bot deck.<br>2. Gain 1 [Glory].<br>3. Return this card. | `LOG`, `GAIN_RESOURCE`, `RETURN_INCIDENT` | yes |
| 2 | Ship | Deploy this Ship; it engages. Send an [Away Team] to a neutral Location. Gain 1 [Military]. | 1. Deploy this Ship; it engages.<br>2. Send an [Away Team] to a neutral Location.<br>3. Gain 1 [Military]. | `DEPLOY`, `ENGAGE`, `SEND_AWAY_TEAM`, `GAIN_SPECIALTY` | yes |
| 3 | Ally | Gain a Business > Person / Ship / Ally. If an Attack is in Bot Discard pile, gain 1 [Military] and 1 [Glory]. Log Duty Officer. Log this card. | 1. Gain a Business > Person / Ship / Ally.<br>2. If an Attack is in Bot Discard pile, gain 1 [Military] and 1 [Glory].<br>3. Log Duty Officer.<br>4. Log this card. | `GAIN_CARD`, `GAIN_SPECIALTY`, `GAIN_RESOURCE`, `LOG` | no |
| 4 | Cargo | Log the top card of the Bot deck. Gain 1 [Influence]. Gain 1 [Military]. Log Duty Officer. Log this card. | 1. Log the top card of the Bot deck.<br>2. Gain 1 [Influence].<br>3. Gain 1 [Military].<br>4. Log Duty Officer.<br>5. Log this card. | `LOG`, `GAIN_SPECIALTY` | yes |
| 5 | Person | Log the top card of the Bot deck. Gain 1 [Influence]. Gain 1 [Military]. Take a Ship / Ally. | 1. Log the top card of the Bot deck.<br>2. Gain 1 [Influence].<br>3. Gain 1 [Military].<br>4. Take a Ship / Ally. | `LOG`, `GAIN_SPECIALTY`, `GAIN_CARD` | no |
| 6 | Directive | If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter, then log this card. Otherwise, gain a Cargo / Ship. | 1. If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter, then log this card.<br>2. Otherwise, gain a Cargo / Ship. | `LOG`, `REMOVE_AWAY_TEAM`, `TAKE_ENCOUNTER`, `GAIN_CARD` | no |
| 7 | Encounter | Gain 1 [Glory]. Gain 1 [Military]. Take a Ship > Ally. Log this card. | 1. Gain 1 [Glory].<br>2. Gain 1 [Military].<br>3. Take a Ship > Ally.<br>4. Log this card. | `GAIN_RESOURCE`, `GAIN_SPECIALTY`, `GAIN_CARD`, `LOG` | no |
| 8 | Location | Gain 1 [Military]. Gain 1 [Glory]. Log Duty Officer. | 1. Gain 1 [Military].<br>2. Gain 1 [Glory].<br>3. Log Duty Officer. | `GAIN_SPECIALTY`, `GAIN_RESOURCE`, `LOG` | yes |

## Five-Year Mission upgrades

Image id: `shran-five-year-mission-upgrades`. Used only in the solo campaign (REQ-CAMP-25 to REQ-CAMP-31).

### WIN

- **A. Common card types you can reinforce:** Weapon / Business
- **B. Alternative bonuses, pick 1:**
  - BOOST: Before drawing the starting hand, find a Location (excluding from your Reserve deck) and immediately free play it.
  - BOOST: Gain 2 [Dilithium].

### LOSS

- **A. Common card types you can reinforce:** Cargo / Human / Tellarite
- **B. Alternative bonuses, pick 1:**
  - BOOST: Gain 1 [Dilithium].
  - REINFORCE: A non-Incident card from your Reserve deck

## Rulings and open questions

- Weapon row: the human chooses between taking an Incident and removing an Away Team (REQ-SOLO-183).
- Attack row: 'you discard the top card of your deck' and 'you take an Incident' are the attack; the Bot's own Incident is not.
- "If able to do both, log ... and remove ... to take top Encounter" rows follow the same reading as the other Bots' Directive rows.

## Tests

- Given a card with a trait on the TRAITS side, when the Bot resolves it, then the first matching trait row is used.
- Given a card with no matching trait, when the Bot resolves it, then the row for its suit on the SUITS side face up is used.
