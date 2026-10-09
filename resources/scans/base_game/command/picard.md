---
id: picard-command
name: Picard Automated Command cards
suit: Automated Command
deck: picard
set: base_game
sides:
  - picard-traits   # picard-traits.jpg
  - picard-no-duty-officer   # picard-no-duty-officer.jpg
  - picard-with-duty-officer   # picard-with-duty-officer.jpg
  - picard-five-year-mission-upgrades   # picard-five-year-mission-upgrades.jpg
---

# Picard Automated Command cards

The Bot playing Picard's Crew deck resolves every card with these rows instead of the card's own text (REQ-SOLO-80 to REQ-SOLO-83). Each row becomes one function in `server/engine/bot/picard.py`, following the Bot action rules in CLAUDE.md.

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

Image id: `picard-traits`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Surprise | Resolve this card's Surprise operation. | 1. Resolve the card's SURPRISE (Bot only) operation instead of any row. |  | yes |
| 2 | Synthetic / Android | Log the top card of the Bot deck. Gain 1 [Research]. Gain 1 [Influence]. If this card is a Person, promote it to Duty Officer. | 1. Log the top card of the Bot deck.<br>2. Gain 1 [Research].<br>3. Gain 1 [Influence].<br>4. If this card is a Person, promote it to Duty Officer. | `LOG`, `GAIN_SPECIALTY`, `PROMOTE` | yes |
| 3 | Klingon | Discard the top 3 cards of the Bot deck. Send an [Away Team] to a neutral Location. **If able, you remove an [Away Team].** Otherwise, gain 1 [Glory] and take an Incident. | 1. Discard the top 3 cards of the Bot deck.<br>2. Send an [Away Team] to a neutral Location.<br>3. If able, you remove an [Away Team].<br>4. Otherwise, gain 1 [Glory] and take an Incident. | `DISCARD`, `SEND_AWAY_TEAM`, `ATTACK`, `REMOVE_AWAY_TEAM`, `GAIN_RESOURCE`, `TAKE_INCIDENT` | no |
| 4 | Alien | Discard the top card of the Bot deck. Gain 1 [Influence]. If Bot has 5+ [Influence], gain 1 [Research] and Cargo. Log this card. | 1. Discard the top card of the Bot deck.<br>2. Gain 1 [Influence].<br>3. If Bot has 5+ [Influence], gain 1 [Research] and Cargo.<br>4. Log this card. | `DISCARD`, `GAIN_SPECIALTY`, `GAIN_CARD`, `LOG` | no |
| 5 | Doctor | Discard the top 2 cards of the Bot deck. If able, return an Incident from discard. Otherwise, gain 2 [Glory] and 1 [Research]. If this card is a Person, promote it to Duty Officer. | 1. Discard the top 2 cards of the Bot deck.<br>2. If able, return an Incident from discard.<br>3. Otherwise, gain 2 [Glory] and 1 [Research].<br>4. If this card is a Person, promote it to Duty Officer. | `DISCARD`, `RETURN_INCIDENT`, `GAIN_RESOURCE`, `GAIN_SPECIALTY`, `PROMOTE` | yes |
| 6 | Attack | Send an [Away Team] to a neutral Location. If able, put a Ship from discard on top of the Bot deck. Otherwise, gain 1 [Influence]. If this card is a Person, promote it to Duty Officer. | 1. Send an [Away Team] to a neutral Location.<br>2. If able, put a Ship from discard on top of the Bot deck.<br>3. Otherwise, gain 1 [Influence].<br>4. If this card is a Person, promote it to Duty Officer. | `SEND_AWAY_TEAM`, `PUT`, `GAIN_SPECIALTY`, `PROMOTE` | yes |

## SUITS WITH NO DUTY OFFICER

Image id: `picard-no-duty-officer`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Log the top card of the Bot deck. Gain a Person. Return this card. | 1. Log the top card of the Bot deck.<br>2. Gain a Person.<br>3. Return this card. | `LOG`, `GAIN_CARD`, `RETURN_INCIDENT` | no |
| 2 | Ship | Deploy this Ship; it explores. If a Person is in Bot Discard pile, send an [Away Team] to a neutral Location. | 1. Deploy this Ship; it explores.<br>2. If a Person is in Bot Discard pile, send an [Away Team] to a neutral Location. | `DEPLOY`, `EXPLORE`, `SEND_AWAY_TEAM` | yes |
| 3 | Ally | Discard the top 2 cards of the Bot deck. For each Person in Bot Discard pile, gain 1 [Influence]. For each Ship in Bot Discard pile, send an [Away Team] to a neutral Location. | 1. Discard the top 2 cards of the Bot deck.<br>2. For each Person in Bot Discard pile, gain 1 [Influence].<br>3. For each Ship in Bot Discard pile, send an [Away Team] to a neutral Location. | `DISCARD`, `GAIN_SPECIALTY`, `SEND_AWAY_TEAM` | yes |
| 4 | Cargo | Discard the top 2 cards of the Bot deck. Gain 2 [Glory]. Take a Person. Log this card. | 1. Discard the top 2 cards of the Bot deck.<br>2. Gain 2 [Glory].<br>3. Take a Person.<br>4. Log this card. | `DISCARD`, `GAIN_RESOURCE`, `GAIN_CARD`, `LOG` | no |
| 5 | Person | Log the top card of the Bot deck. Gain 1 [Research] / [Influence] (whichever is lower). Send an [Away Team] to a neutral Location. Promote this card to Duty Officer. | 1. Log the top card of the Bot deck.<br>2. Gain 1 [Research] / [Influence] (whichever is lower).<br>3. Send an [Away Team] to a neutral Location.<br>4. Promote this card to Duty Officer. | `LOG`, `GAIN_SPECIALTY`, `SEND_AWAY_TEAM`, `PROMOTE` | yes |
| 6 | Directive | If able, gain a Klingon. Otherwise, gain a Ship / Ally and take an Incident. Gain 1 [Research] / [Influence] (whichever is lower). Send an [Away Team] to a neutral Location. | 1. If able, gain a Klingon.<br>2. Otherwise, gain a Ship / Ally and take an Incident.<br>3. Gain 1 [Research] / [Influence] (whichever is lower).<br>4. Send an [Away Team] to a neutral Location. | `GAIN_CARD`, `TAKE_INCIDENT`, `GAIN_SPECIALTY`, `SEND_AWAY_TEAM` | no |
| 7 | Encounter | Log the top 2 cards of the Bot deck. Take a Ship. Log this card. | 1. Log the top 2 cards of the Bot deck.<br>2. Take a Ship.<br>3. Log this card. | `LOG`, `GAIN_CARD` | no |
| 8 | Location | Log the top card of the Bot deck. Discard the top 3 cards of the Bot deck. | 1. Log the top card of the Bot deck.<br>2. Discard the top 3 cards of the Bot deck. | `LOG`, `DISCARD` | yes |

## SUITS WITH DUTY OFFICER

Image id: `picard-with-duty-officer`.

Used while the Bot has a Duty Officer. Flip back when it is dismissed or logged (REQ-SOLO-91 to REQ-SOLO-95).

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Discard the top 2 cards of the Bot deck. Gain 1 [Research]. Return this card. | 1. Discard the top 2 cards of the Bot deck.<br>2. Gain 1 [Research].<br>3. Return this card. | `DISCARD`, `GAIN_SPECIALTY`, `RETURN_INCIDENT` | yes |
| 2 | Ship | Gain 1 [Influence]. Deploy this Ship; it explores. Send an [Away Team] to a neutral Location. | 1. Gain 1 [Influence].<br>2. Deploy this Ship; it explores.<br>3. Send an [Away Team] to a neutral Location. | `GAIN_SPECIALTY`, `DEPLOY`, `EXPLORE`, `SEND_AWAY_TEAM` | yes |
| 3 | Ally | Discard the top card of the Bot deck. Gain a Klingon > Person / Ship / Ally. Log Duty Officer. Log this card. | 1. Discard the top card of the Bot deck.<br>2. Gain a Klingon > Person / Ship / Ally.<br>3. Log Duty Officer.<br>4. Log this card. | `DISCARD`, `GAIN_CARD`, `LOG` | no |
| 4 | Cargo | Log the top card of the Bot deck. Discard the top 2 cards of the Bot deck. Gain a Ship. Deploy the gained Ship; it explores. Log Duty Officer. | 1. Log the top card of the Bot deck.<br>2. Discard the top 2 cards of the Bot deck.<br>3. Gain a Ship.<br>4. Deploy the gained Ship; it explores.<br>5. Log Duty Officer. | `LOG`, `DISCARD`, `GAIN_CARD`, `DEPLOY`, `EXPLORE` | no |
| 5 | Person | Log the top card of the Bot deck. Gain 1 [Research] / [Influence] (whichever is lower). Send an [Away Team] to a neutral Location. | 1. Log the top card of the Bot deck.<br>2. Gain 1 [Research] / [Influence] (whichever is lower).<br>3. Send an [Away Team] to a neutral Location. | `LOG`, `GAIN_SPECIALTY`, `SEND_AWAY_TEAM` | yes |
| 6 | Directive | If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter then log this card. Otherwise, gain a [Research Focus] > Alien > Cargo / Ally. | 1. If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter then log this card.<br>2. Otherwise, gain a [Research Focus] > Alien > Cargo / Ally. | `LOG`, `REMOVE_AWAY_TEAM`, `TAKE_ENCOUNTER`, `GAIN_CARD` | no |
| 7 | Encounter | Gain 1 [Research] / [Influence] (whichever is higher). Take a Klingon > Ally > Ship. Log this card. | 1. Gain 1 [Research] / [Influence] (whichever is higher).<br>2. Take a Klingon > Ally > Ship.<br>3. Log this card. | `GAIN_SPECIALTY`, `GAIN_CARD`, `LOG` | no |
| 8 | Location | Log the top 2 cards of the Bot deck. Gain 1 [Research]. Log Duty Officer. | 1. Log the top 2 cards of the Bot deck.<br>2. Gain 1 [Research].<br>3. Log Duty Officer. | `LOG`, `GAIN_SPECIALTY` | yes |

## Five-Year Mission upgrades

Image id: `picard-five-year-mission-upgrades`. Used only in the solo campaign (REQ-CAMP-25 to REQ-CAMP-31).

### WIN

- **A. Common card types you can reinforce:** Alien / Transcendent
- **B. Alternative bonuses, pick 1:**
  - BOOST: Gain 3 [Research].
  - BOOST: Before drawing the starting hand, find two cards (excluding from your Reserve deck).

### LOSS

- **A. Common card types you can reinforce:** Ally / Alien / Synthetic
- **B. Alternative bonuses, pick 1:**
  - BOOST: Gain 1 [Research].
  - BOOST: Before drawing the starting hand, find one card (excluding from your Reserve deck).

## Rulings and open questions

- Klingon row: 'you remove an [Away Team]' is read as from the Location the Bot just sent to, the human's choice if that is unclear.
- "If able to do both, log ... and remove ... to take top Encounter" rows follow the same reading as the other Bots' Directive rows.
- The rulings for this Bot's rows were confirmed on 2026-10-09; they are listed in requirements/23-core-box.md REQ-CORE-64.

## Tests

- Given a card with a trait on the TRAITS side, when the Bot resolves it, then the first matching trait row is used.
- Given a card with no matching trait, when the Bot resolves it, then the row for its suit on the SUITS side face up is used.
