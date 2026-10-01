---
id: pike-command
name: Pike Automated Command cards
suit: Automated Command
deck: pike
set: second_contact
sides:
  - pike-traits   # pike-traits.jpg
  - pike-no-duty-officer   # pike-no-duty-officer.jpg
  - pike-with-duty-officer   # pike-with-duty-officer.jpg
  - pike-five-year-mission-upgrades   # pike-five-year-mission-upgrades.jpg
---

# Pike Automated Command cards

The Bot playing Pike's Crew deck resolves every card with these rows instead of the card's own text (REQ-SOLO-80 to REQ-SOLO-83). Each row becomes one function in `server/engine/bot/pike.py`, following the Bot action rules in CLAUDE.md.

## How a card is resolved

1. If the card has the Surprise trait, resolve its SURPRISE operation and stop (REQ-SOLO-87).
2. Otherwise check the TRAITS rows from top to bottom. The first row with a trait the card has is used. A Wildcard card matches the first trait row (REQ-SOLO-82).
3. If no trait row matches, use the row for the card's suit on whichever SUITS side is face up: WITH NO DUTY OFFICER, or WITH DUTY OFFICER.
4. "Continue resolution" stops the current row and finds the next matching row, trait rows first, then suits (REQ-SOLO-120).
5. A Location still in the Staging Area afterwards moves to the Bot's Control Area (REQ-SOLO-89).

Text shown **in bold** is resolved by the human player. On the card, bold red text is an attack, which the human may cancel; bold black text affects the human without attacking. Rows with an attack list the `ATTACK` action (REQ-SOLO-180 to REQ-SOLO-185).

## Special rule

When a card with one or more [Research]/[Influence]/[Military] Skill icons is resolved, the Bot gains 1 on the corresponding Specialty track. If multiple different Skills (or an [Any Skill]) are present, it gains whichever is higher.

## TRAITS

Image id: `pike-traits`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Surprise | Resolve this card's Surprise operation. | 1. Resolve the card's SURPRISE (Bot only) operation instead of any row. |  | yes |
| 2 | Time Travel | If this card is a Person, discard the top card of the Bot deck, take an Incident, gain a Person / Ship, and promote this card to Duty Officer. Otherwise, if this card is a Cargo, gain an Incident and resolve the top card of the Supplement deck, then log that card. Otherwise, gain 3 [Glory] and log this card. | 1. If this card is a Person, discard the top card of the Bot deck, take an Incident, gain a Person / Ship, and promote this card to Duty Officer..<br>2. Otherwise, if this card is a Cargo, gain an Incident and resolve the top card of the Supplement deck, then log that card..<br>3. Otherwise, gain 3 [Glory] and log this card. | `DISCARD`, `TAKE_INCIDENT`, `GAIN_CARD`, `PROMOTE`, `RESOLVE_CARD`, `LOG`, `GAIN_RESOURCE` | no |
| 3 | Engineer | Discard the top 2 cards of the Bot deck. Send an [Away Team] to a neutral Location. Resolve a Cargo / Ship from the Bot Discard if able; otherwise continue resolution. | 1. Discard the top 2 cards of the Bot deck..<br>2. Send an [Away Team] to a neutral Location..<br>3. Resolve a Cargo / Ship from the Bot Discard if able; otherwise continue resolution. | `DISCARD`, `SEND_AWAY_TEAM`, `RESOLVE_CARD`, `CONTINUE_RESOLUTION` | no |
| 4 | Doctor | If able, return an Incident from the Bot Discard; otherwise (if able) send an [Away Team] to a Location where the Bot has a Ship. If Bot has 6 or more [Research], gain a Time Travel > Doctor > Person. Otherwise, gain 1 [Research] and continue resolution. | 1. If able, return an Incident from the Bot Discard; otherwise (if able) send an [Away Team] to a Location where the Bot has a Ship..<br>2. If Bot has 6 or more [Research], gain a Time Travel > Doctor > Person..<br>3. Otherwise, gain 1 [Research] and continue resolution. | `RETURN_INCIDENT`, `SEND_AWAY_TEAM`, `GAIN_CARD`, `GAIN_SPECIALTY`, `CONTINUE_RESOLUTION` | no |
| 5 | Telepath | Discard the top 3 cards of the Bot deck. Discard the top card of the Supplement deck. | 1. Discard the top 3 cards of the Bot deck..<br>2. Discard the top card of the Supplement deck. | `DISCARD` | yes |
| 6 | Attack / Shady | Gain an Incident. Log this card. | 1. Gain an Incident..<br>2. Log this card. | `TAKE_INCIDENT`, `LOG` | no |

## SUITS WITH NO DUTY OFFICER

Image id: `pike-no-duty-officer`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | If able, gain [Research Focus]/[Influence Focus]; otherwise gain 1 [Research] / [Influence] / [Military] (whichever is lower). Return this card. | 1. If able, gain [Research Focus]/[Influence Focus]; otherwise gain 1 [Research] / [Influence] / [Military] (whichever is lower)..<br>2. Return this card. | `GAIN_CARD`, `GAIN_SPECIALTY`, `RETURN_INCIDENT` | no |
| 2 | Ship | Discard the top 3 cards of the Bot deck. Deploy this Ship; it explores. If a Person is in the Bot Discard pile, send an [Away Team] to a neutral Location. | 1. Discard the top 3 cards of the Bot deck..<br>2. Deploy this Ship; it explores..<br>3. If a Person is in the Bot Discard pile, send an [Away Team] to a neutral Location. | `DISCARD`, `DEPLOY`, `EXPLORE`, `SEND_AWAY_TEAM` | no |
| 3 | Ally | Discard the top 2 cards of the Bot deck. Gain a Person. Gain 1 [Research] / [Influence] / [Military] (whichever is lower). Log this card. | 1. Discard the top 2 cards of the Bot deck..<br>2. Gain a Person..<br>3. Gain 1 [Research] / [Influence] / [Military] (whichever is lower)..<br>4. Log this card. | `DISCARD`, `GAIN_CARD`, `GAIN_SPECIALTY`, `LOG` | no |
| 4 | Cargo | Gain 1 [Influence]. Send an [Away Team] to a neutral Location. Discard the top 2 cards of the Bot deck. Log a non-Time Travel Person from the Bot Discard (if able) to gain 1 [Glory]. Log this card. | 1. Gain 1 [Influence]..<br>2. Send an [Away Team] to a neutral Location..<br>3. Discard the top 2 cards of the Bot deck..<br>4. Log a non-Time Travel Person from the Bot Discard (if able) to gain 1 [Glory]..<br>5. Log this card. | `GAIN_SPECIALTY`, `SEND_AWAY_TEAM`, `DISCARD`, `LOG`, `GAIN_RESOURCE` | yes |
| 5 | Person | If there is no Starfleet in the Bot Discard, take a [Research Focus]/[Influence Focus] > Starfleet / Augment > Ship; otherwise send an [Away Team] to a neutral Location. Promote this card to Duty Officer. | 1. If there is no Starfleet in the Bot Discard, take a [Research Focus]/[Influence Focus] > Starfleet / Augment > Ship; otherwise send an [Away Team] to a neutral Location..<br>2. Promote this card to Duty Officer. | `GAIN_CARD`, `SEND_AWAY_TEAM`, `PROMOTE` | no |
| 6 | Directive | Discard the top 2 cards of the Bot deck. Resolve a Ship from the Bot Discard, if able; otherwise take an Incident and send an [Away Team] to a neutral Location. | 1. Discard the top 2 cards of the Bot deck..<br>2. Resolve a Ship from the Bot Discard, if able; otherwise take an Incident and send an [Away Team] to a neutral Location. | `DISCARD`, `RESOLVE_CARD`, `TAKE_INCIDENT`, `SEND_AWAY_TEAM` | no |
| 7 | Encounter | Discard the top 3 cards of the Bot deck. Take a Time Travel > Doctor > [Research Focus]/[Influence Focus]/[Military Focus] > Person. Discard the top card of the Supplement deck. Log this card. | 1. Discard the top 3 cards of the Bot deck..<br>2. Take a Time Travel > Doctor > [Research Focus]/[Influence Focus]/[Military Focus] > Person..<br>3. Discard the top card of the Supplement deck..<br>4. Log this card. | `DISCARD`, `GAIN_CARD`, `LOG` | no |
| 8 | Location | Discard the top 2 cards of the Bot deck. Gain 1 [Glory]. If this card is a Starbase, send an [Away Team] to a neutral Location. | 1. Discard the top 2 cards of the Bot deck..<br>2. Gain 1 [Glory]..<br>3. If this card is a Starbase, send an [Away Team] to a neutral Location. | `DISCARD`, `GAIN_RESOURCE`, `SEND_AWAY_TEAM` | yes |

## SUITS WITH DUTY OFFICER

Image id: `pike-with-duty-officer`.

Used while the Bot has a Duty Officer. Flip back when it is dismissed or logged (REQ-SOLO-91 to REQ-SOLO-95).

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Discard the top card of the Bot deck. If Bot has 10 or more [Research]/[Influence]/[Military] and if able, gain a card with matching Focus, including from the Junk; otherwise gain 1 [Research] and 1 [Influence]. Return this card. | 1. Discard the top card of the Bot deck..<br>2. If Bot has 10 or more [Research]/[Influence]/[Military] and if able, gain a card with matching Focus, including from the Junk; otherwise gain 1 [Research] and 1 [Influence]..<br>3. Return this card. | `DISCARD`, `GAIN_CARD`, `GAIN_SPECIALTY`, `RETURN_INCIDENT` | no |
| 2 | Ship | For each Starbase and Engineer in play, discard the top card of the Bot deck. Deploy this Ship; it engages. Send an [Away Team] to a neutral Location. | 1. For each Starbase and Engineer in play, discard the top card of the Bot deck..<br>2. Deploy this Ship; it engages..<br>3. Send an [Away Team] to a neutral Location. | `DISCARD`, `DEPLOY`, `ENGAGE`, `SEND_AWAY_TEAM` | no |
| 3 | Ally | Gain 1 [Influence] / [Military] (whichever is lower). If Bot has 8 or fewer [Research], gain a Ship from the top of the deck and gain 1 [Research]; otherwise take Time Travel > Doctor > Person, and gain 1 [Glory] for each Doctor in play or in the Bot Discard. Log this card and dismiss Duty Officer. | 1. Gain 1 [Influence] / [Military] (whichever is lower)..<br>2. If Bot has 8 or fewer [Research], gain a Ship from the top of the deck and gain 1 [Research]; otherwise take Time Travel > Doctor > Person, and gain 1 [Glory] for each Doctor in play or in the Bot Discard..<br>3. Log this card and dismiss Duty Officer. | `GAIN_SPECIALTY`, `GAIN_CARD`, `GAIN_RESOURCE`, `LOG`, `DISMISS` | no |
| 4 | Cargo | Discard the top 3 cards of the Bot deck. Gain a [Research Focus]/[Influence Focus] > Ally. Dismiss Duty Officer. | 1. Discard the top 3 cards of the Bot deck..<br>2. Gain a [Research Focus]/[Influence Focus] > Ally..<br>3. Dismiss Duty Officer. | `DISCARD`, `GAIN_CARD`, `DISMISS` | no |
| 5 | Person | Junk the most valuable card in the Market (ignoring any with tokens). If Bot has 6 or more [Influence], gain an [Influence Focus] / Ship / Ally and dismiss Duty Officer; otherwise gain 2 [Influence]. | 1. Junk the most valuable card in the Market (ignoring any with tokens)..<br>2. If Bot has 6 or more [Influence], gain an [Influence Focus] / Ship / Ally and dismiss Duty Officer; otherwise gain 2 [Influence]. | `JUNK`, `GAIN_CARD`, `DISMISS`, `GAIN_SPECIALTY` | no |
| 6 | Directive | If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter, then log this card. Otherwise gain 1 [Research] and gain a card with any Research, Influence or Military Skill or Focus icon. | 1. If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter, then log this card..<br>2. Otherwise gain 1 [Research] and gain a card with any Research, Influence or Military Skill or Focus icon. | `LOG`, `REMOVE_AWAY_TEAM`, `TAKE_ENCOUNTER`, `GAIN_SPECIALTY`, `GAIN_CARD` | no |
| 7 | Encounter | Log the top card of the Bot deck. Gain 1 [Military]. Gain 1 [Influence]. Take an Ally. Resolve the top card of the Supplement deck. Log this card. | 1. Log the top card of the Bot deck..<br>2. Gain 1 [Military]..<br>3. Gain 1 [Influence]..<br>4. Take an Ally..<br>5. Resolve the top card of the Supplement deck..<br>6. Log this card. | `LOG`, `GAIN_SPECIALTY`, `GAIN_CARD`, `RESOLVE_CARD` | no |
| 8 | Location | Discard the top 3 cards of the Bot deck. Gain 1 [Influence]. If Duty Officer is Time Travel, dismiss it; otherwise log it. | 1. Discard the top 3 cards of the Bot deck..<br>2. Gain 1 [Influence]..<br>3. If Duty Officer is Time Travel, dismiss it; otherwise log it. | `DISCARD`, `GAIN_SPECIALTY`, `DISMISS`, `LOG` | yes |

## Five-Year Mission upgrades

Image id: `pike-five-year-mission-upgrades`. Used only in the solo campaign (REQ-CAMP-25 to REQ-CAMP-31).

### WIN

- **A. Common card types you can reinforce:** Time Travel / Doctor
- **B. Alternative bonuses, pick 1:**
  - BOOST: Before drawing the starting hand, take an Incident to enlist a Development.
  - BOOST: Gain 1 [Research], 1 [Influence], and 1 [Military].

### LOSS

- **A. Common card types you can reinforce:** Ship
- **B. Alternative bonuses, pick 1:**
  - REINFORCE: A card with [Research]/[Influence]/[Military] from your Available cards or Reserve deck.
  - BOOST: After drawing the starting hand, free play a non-Time Travel card, then recall it.

## Rulings and open questions

- The Directive row with a Duty Officer lists six icons, Skill and Focus for each Specialty; read as gaining a card with any one of them.
- Pike's special rule mirrors his Status card for the human.

## Tests

- Given the Bot resolves a card with a Research Skill icon, it gains 1 Research before the matching row.
