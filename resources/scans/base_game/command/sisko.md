---
id: sisko-command
name: Sisko Automated Command cards
suit: Automated Command
deck: sisko
set: base_game
sides:
  - sisko-traits   # sisko-traits.jpg
  - sisko-no-duty-officer   # sisko-no-duty-officer.jpg
  - sisko-with-duty-officer   # sisko-with-duty-officer.jpg
  - sisko-five-year-mission-upgrades   # sisko-five-year-mission-upgrades.jpg
---

# Sisko Automated Command cards

The Bot playing Sisko's Crew deck resolves every card with these rows instead of the card's own text (REQ-SOLO-80 to REQ-SOLO-83). Each row becomes one function in `server/engine/bot/sisko.py`, following the Bot action rules in CLAUDE.md.

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

Image id: `sisko-traits`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Surprise | Resolve this card's Surprise operation. | 1. Resolve the card's SURPRISE (Bot only) operation instead of any row. |  | yes |
| 2 | Transcendent | If able, gain a Bajoran > Dominion > Changeling. Otherwise, gain 2 [Military] and 1 [Glory]. | 1. If able, gain a Bajoran > Dominion > Changeling.<br>2. Otherwise, gain 2 [Military] and 1 [Glory]. | `GAIN_CARD`, `GAIN_SPECIALTY`, `GAIN_RESOURCE` | no |
| 3 | Starbase | Discard the top 3 cards of the Bot deck. If this card is a Ship, deploy this card. Otherwise, gain 1 [Glory]. If able, resolve a Person from Bot Discard pile. Otherwise gain 2 [Influence]. | 1. Discard the top 3 cards of the Bot deck.<br>2. If this card is a Ship, deploy this card.<br>3. Otherwise, gain 1 [Glory].<br>4. If able, resolve a Person from Bot Discard pile.<br>5. Otherwise gain 2 [Influence]. | `DISCARD`, `DEPLOY`, `GAIN_RESOURCE`, `RESOLVE_CARD`, `GAIN_SPECIALTY` | no |
| 4 | Bajoran | Gain 1 [Influence] and 1 [Military]. Take an Incident. If an Ally is in Bot Discard pile, send 2 [Away Team] to a neutral Location. Otherwise, **you dismiss (one of) your Duty Officer(s)** and the Bot gains 2 [Military]. If this card is a Person, promote it to Duty Officer. | 1. Gain 1 [Influence] and 1 [Military].<br>2. Take an Incident.<br>3. If an Ally is in Bot Discard pile, send 2 [Away Team] to a neutral Location.<br>4. Otherwise, you dismiss (one of) your Duty Officer(s) and the Bot gains 2 [Military].<br>5. If this card is a Person, promote it to Duty Officer. | `GAIN_SPECIALTY`, `TAKE_INCIDENT`, `SEND_AWAY_TEAM`, `ATTACK`, `DISMISS`, `PROMOTE` | no |
| 5 | Changeling / Dominion | Log the top card of the Bot deck. Resolve the top card of the Bot deck. If this card is a Person, promote it to Duty Officer. | 1. Log the top card of the Bot deck.<br>2. Resolve the top card of the Bot deck.<br>3. If this card is a Person, promote it to Duty Officer. | `LOG`, `RESOLVE_CARD`, `PROMOTE` | no |
| 6 | Attack | Send an [Away Team] to a neutral Starbase > Starfleet > Location. If this card is a Ship, **you discard a card** and deploy this Ship; it engages. Otherwise, gain 2 [Military]. | 1. Send an [Away Team] to a neutral Starbase > Starfleet > Location.<br>2. If this card is a Ship, you discard a card and deploy this Ship; it engages.<br>3. Otherwise, gain 2 [Military]. | `SEND_AWAY_TEAM`, `ATTACK`, `DISCARD`, `DEPLOY`, `ENGAGE`, `GAIN_SPECIALTY` | no |

## SUITS WITH NO DUTY OFFICER

Image id: `sisko-no-duty-officer`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Discard the top card of the Bot deck. Gain a [Military Focus] > [Influence Focus] > Person / Ally. Return this card. | 1. Discard the top card of the Bot deck.<br>2. Gain a [Military Focus] > [Influence Focus] > Person / Ally.<br>3. Return this card. | `DISCARD`, `GAIN_CARD`, `RETURN_INCIDENT` | no |
| 2 | Ship | Discard the top 3 cards of the Bot deck. Deploy this Ship; it explores. If a Person is in Bot Discard pile, send an [Away Team] to a neutral Starbase > Starfleet > Location. | 1. Discard the top 3 cards of the Bot deck.<br>2. Deploy this Ship; it explores.<br>3. If a Person is in Bot Discard pile, send an [Away Team] to a neutral Starbase > Starfleet > Location. | `DISCARD`, `DEPLOY`, `EXPLORE`, `SEND_AWAY_TEAM` | yes |
| 3 | Ally | Gain 1 [Glory]. Discard the top 2 cards of the Bot deck. For each Person in Bot Discard pile, gain 1 [Influence]. For each Ship in Bot Discard pile, send an [Away Team] to a neutral Starbase > Starfleet > Location. | 1. Gain 1 [Glory].<br>2. Discard the top 2 cards of the Bot deck.<br>3. For each Person in Bot Discard pile, gain 1 [Influence].<br>4. For each Ship in Bot Discard pile, send an [Away Team] to a neutral Starbase > Starfleet > Location. | `GAIN_RESOURCE`, `DISCARD`, `GAIN_SPECIALTY`, `SEND_AWAY_TEAM` | yes |
| 4 | Cargo | Discard the top 2 cards of the Bot deck. If able, log a Person from Bot Discard pile. Gain 1 [Glory]. Gain 1 [Influence]. Gain 1 [Military]. Send an [Away Team] to a neutral Location. | 1. Discard the top 2 cards of the Bot deck.<br>2. If able, log a Person from Bot Discard pile.<br>3. Gain 1 [Glory].<br>4. Gain 1 [Influence].<br>5. Gain 1 [Military].<br>6. Send an [Away Team] to a neutral Location. | `DISCARD`, `LOG`, `GAIN_RESOURCE`, `GAIN_SPECIALTY`, `SEND_AWAY_TEAM` | yes |
| 5 | Person | Gain 1 [Influence]. Send an [Away Team] to a neutral Location. Promote this card to Duty Officer. | 1. Gain 1 [Influence].<br>2. Send an [Away Team] to a neutral Location.<br>3. Promote this card to Duty Officer. | `GAIN_SPECIALTY`, `SEND_AWAY_TEAM`, `PROMOTE` | yes |
| 6 | Directive | Discard the top 3 cards of the Bot deck. If able, log a Person from Bot Discard pile to send an [Away Team] to a neutral Location. Otherwise, gain 1 [Influence] / [Military] (whichever is lower) and gain a Person. | 1. Discard the top 3 cards of the Bot deck.<br>2. If able, log a Person from Bot Discard pile to send an [Away Team] to a neutral Location.<br>3. Otherwise, gain 1 [Influence] / [Military] (whichever is lower) and gain a Person. | `DISCARD`, `LOG`, `SEND_AWAY_TEAM`, `GAIN_SPECIALTY`, `GAIN_CARD` | no |
| 7 | Encounter | Discard the top 3 cards of the Bot deck. Take an [Influence Focus] > Person. Log this card. | 1. Discard the top 3 cards of the Bot deck.<br>2. Take an [Influence Focus] > Person.<br>3. Log this card. | `DISCARD`, `GAIN_CARD`, `LOG` | no |
| 8 | Location | Log the top card of the Bot deck. Discard the top 3 cards of the Bot deck. Gain 1 [Military]. If able, return a Ship from Bot Discard pile to top of the Bot deck. | 1. Log the top card of the Bot deck.<br>2. Discard the top 3 cards of the Bot deck.<br>3. Gain 1 [Military].<br>4. If able, return a Ship from Bot Discard pile to top of the Bot deck. | `LOG`, `DISCARD`, `GAIN_SPECIALTY`, `PUT` | yes |

## SUITS WITH DUTY OFFICER

Image id: `sisko-with-duty-officer`.

Used while the Bot has a Duty Officer. Flip back when it is dismissed or logged (REQ-SOLO-91 to REQ-SOLO-95).

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Take a [Military Focus] > Ship > Cargo. Gain 1 [Military]. Return this card. | 1. Take a [Military Focus] > Ship > Cargo.<br>2. Gain 1 [Military].<br>3. Return this card. | `GAIN_CARD`, `GAIN_SPECIALTY`, `RETURN_INCIDENT` | no |
| 2 | Ship | If able, log a Starbase in play to resolve the top card of the Supplement deck. Deploy this Ship; it explores. Send an [Away Team] to a neutral Location. | 1. If able, log a Starbase in play to resolve the top card of the Supplement deck.<br>2. Deploy this Ship; it explores.<br>3. Send an [Away Team] to a neutral Location. | `LOG`, `RESOLVE_CARD`, `DEPLOY`, `EXPLORE`, `SEND_AWAY_TEAM` | no |
| 3 | Ally | Gain 1 [Influence] / [Military] (whichever is lower). Gain a Cargo > Ship / Ally. Log this card. | 1. Gain 1 [Influence] / [Military] (whichever is lower).<br>2. Gain a Cargo > Ship / Ally.<br>3. Log this card. | `GAIN_SPECIALTY`, `GAIN_CARD`, `LOG` | no |
| 4 | Cargo | Discard the top 3 cards of the Bot deck. Gain 1 [Military]. Gain an [Influence Focus] > [Military Focus] > Ship. Log Duty Officer. | 1. Discard the top 3 cards of the Bot deck.<br>2. Gain 1 [Military].<br>3. Gain an [Influence Focus] > [Military Focus] > Ship.<br>4. Log Duty Officer. | `DISCARD`, `GAIN_SPECIALTY`, `GAIN_CARD`, `LOG` | no |
| 5 | Person | Discard the top 3 cards of the Bot deck. Gain 1 [Influence] / [Military] (whichever is lower). Gain a Ship / [Influence Focus]. | 1. Discard the top 3 cards of the Bot deck.<br>2. Gain 1 [Influence] / [Military] (whichever is lower).<br>3. Gain a Ship / [Influence Focus]. | `DISCARD`, `GAIN_SPECIALTY`, `GAIN_CARD` | no |
| 6 | Directive | If able to do both, log a controlled Location (not a Starbase) and remove 2 [Away Team] to take top Encounter and log this card. Otherwise, send an [Away Team] to a neutral Location, gain 1 [Influence], and dismiss Duty Officer. | 1. If able to do both, log a controlled Location (not a Starbase) and remove 2 [Away Team] to take top Encounter and log this card.<br>2. Otherwise, send an [Away Team] to a neutral Location, gain 1 [Influence], and dismiss Duty Officer. | `LOG`, `REMOVE_AWAY_TEAM`, `TAKE_ENCOUNTER`, `SEND_AWAY_TEAM`, `GAIN_SPECIALTY`, `DISMISS` | no |
| 7 | Encounter | Discard the top card of the Bot deck. Gain 1 [Military]. Gain 1 [Influence]. Take a Ship / Ally. | 1. Discard the top card of the Bot deck.<br>2. Gain 1 [Military].<br>3. Gain 1 [Influence].<br>4. Take a Ship / Ally. | `DISCARD`, `GAIN_SPECIALTY`, `GAIN_CARD` | no |
| 8 | Location | Log the top card of the Bot deck. Discard the top 3 cards of the Bot deck. Gain 1 [Influence]. Log Duty Officer. | 1. Log the top card of the Bot deck.<br>2. Discard the top 3 cards of the Bot deck.<br>3. Gain 1 [Influence].<br>4. Log Duty Officer. | `LOG`, `DISCARD`, `GAIN_SPECIALTY` | yes |

## Five-Year Mission upgrades

Image id: `sisko-five-year-mission-upgrades`. Used only in the solo campaign (REQ-CAMP-25 to REQ-CAMP-31).

### WIN

- **A. Common card types you can reinforce:** Anomaly / Scientist
- **B. Alternative bonuses, pick 1:**
  - BOOST: Gain 3 [Influence].
  - BOOST: Gain 2 [Latinum].

### LOSS

- **A. Common card types you can reinforce:** Cargo / Ally / Person
- **B. Alternative bonuses, pick 1:**
  - BOOST: Gain 1 [Influence].
  - BOOST: Gain 1 [Dilithium].

## Rulings and open questions

- Solo setup: Deep Space 9 (Deployed) and Bajor (Controlled Location) go on top of the Bot deck like any such cards (REQ-SOLO-28). Deep Space 9 has the Starbase trait, so it resolves through the Starbase row and is deployed without exploring.
- 'Starbase in play' on the Ship row with a Duty Officer is one of the Bot's own cards in play.
- The folded-corner icons in the gain lists are Focus icons, read as [Military Focus] and [Influence Focus].
- "If able to do both, log ... and remove ... to take top Encounter" rows follow the same reading as the other Bots' Directive rows.

## Tests

- Given a card with a trait on the TRAITS side, when the Bot resolves it, then the first matching trait row is used.
- Given a card with no matching trait, when the Bot resolves it, then the row for its suit on the SUITS side face up is used.
