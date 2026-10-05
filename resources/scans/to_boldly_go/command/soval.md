---
id: soval-command
name: Soval Automated Command cards
suit: Automated Command
deck: soval
set: to_boldly_go
sides:
  - soval-traits   # soval-traits.jpg
  - soval-no-duty-officer   # soval-no-duty-officer.jpg
  - soval-with-duty-officer   # soval-with-duty-officer.jpg
  - soval-five-year-mission-upgrades   # soval-five-year-mission-upgrades.jpg
---

# Soval Automated Command cards

The Bot playing Soval's Crew deck resolves every card with these rows instead of the card's own text (REQ-SOLO-80 to REQ-SOLO-83). Each row becomes one function in `server/engine/bot/soval.py`, following the Bot action rules in CLAUDE.md.

## How a card is resolved

1. If the card has the Surprise trait, resolve its SURPRISE operation and stop (REQ-SOLO-87).
2. Otherwise check the TRAITS rows from top to bottom. The first row with a trait the card has is used. A Wildcard card matches the first trait row (REQ-SOLO-82).
3. If no trait row matches, use the row for the card's suit on whichever SUITS side is face up: WITH NO DUTY OFFICER, or WITH DUTY OFFICER.
4. "Continue resolution" stops the current row and finds the next matching row, trait rows first, then suits (REQ-SOLO-120).
5. A Location still in the Staging Area afterwards moves to the Bot's Control Area (REQ-SOLO-89).

Text shown **in bold** is resolved by the human player. On the card, bold red text is an attack, which the human may cancel; bold black text affects the human without attacking. Rows with an attack list the `ATTACK` action (REQ-SOLO-180 to REQ-SOLO-185).

## Special rule

If a card with Path of Surak would be logged when logging the top card of the Bot deck, discard it instead.

## TRAITS

Image id: `soval-traits`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Surprise | Resolve this card's Surprise operation. | 1. Resolve the card's SURPRISE (Bot only) operation instead of any row. |  | yes |
| 2 | Telepath | **You may return an Incident from your hand or Discard pile.** If you do, resolve the top card of the Bot deck. If this card is a Person, promote it to Duty Officer. Continue resolution. | 1. The human may return an Incident from their hand or Discard pile.<br>2. If they did, the Bot resolves the top card of the Bot deck (REQ-SOLO-100).<br>3. If this card is a Person, promote it.<br>4. Continue resolution. | `RETURN_INCIDENT`, `RESOLVE_CARD`, `PROMOTE`, `CONTINUE_RESOLUTION` | no |
| 3 | Scientist / Anomaly | Gain 1 [Glory]. Take [Research] / [Influence] / [Military], if able. Otherwise gain 2 [Research] and discard the top card of the Bot deck. If this card is a Ship, deploy it; it explores. | 1. Gain 1 Glory.<br>2. Take the most valuable Market card with a Research, Influence or Military Skill icon, onto the Bot deck.<br>3. If there is none: gain 2 Research and discard the top card of the Bot deck.<br>4. If this card is a Ship, deploy it and explore. | `GAIN_RESOURCE`, `GAIN_CARD`, `GAIN_SPECIALTY`, `DISCARD`, `DEPLOY`, `EXPLORE` | no |
| 4 | Human / Engineer | Discard the top 3 cards of the Bot deck. Gain 1 [Research] / [Influence] / [Military] (whichever is lower). If this card is a Person, promote it to Duty Officer. | 1. Discard the top 3 cards of the Bot deck.<br>2. Gain 1 in the Bot's lowest Specialty; ties go Research, Influence, Military (REQ-SOLO-85).<br>3. If this card is a Person, promote it. | `DISCARD`, `GAIN_SPECIALTY`, `PROMOTE` | yes |
| 5 | Path of Surak | Take top Encounter. If this card is Cargo resolve the top card of the Bot deck and log this card. | 1. Take the top Encounter onto the Bot deck.<br>2. If this card is a Cargo: resolve the top card of the Bot deck, then log this card. | `TAKE_ENCOUNTER`, `RESOLVE_CARD`, `LOG` | no |
| 6 | Attack | If Bot has 8 or fewer [Military], **you remove an [Away Team] from a neutral Location, if able**, then send a Bot [Away Team] to the same Location, if able. If either option failed, gain 2 [Military]. If Bot has 9+ [Military], the Bot takes control of a neutral Location (excluding ones **you have secured**), then log this card. | 1. If the Bot's Military is 8 or less: the human removes one of their Away Teams from a neutral Location of their choice (attack part); then the Bot sends an Away Team to that Location; if either part failed, the Bot gains 2 Military.<br>2. If the Bot's Military is 9 or more: the Bot takes control of the most valuable neutral Location the human has not secured, then logs this card. | `ATTACK`, `REMOVE_AWAY_TEAM`, `SEND_AWAY_TEAM`, `GAIN_SPECIALTY`, `TAKE_CONTROL`, `LOG` | no |

## SUITS WITH NO DUTY OFFICER

Image id: `soval-no-duty-officer`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Log the top card of the Bot deck. Gain a Person. Return this card. | 1. Log the top card of the Bot deck (special rule applies).<br>2. Gain the most valuable Market Person.<br>3. Return this card to the Incident deck. | `LOG`, `GAIN_CARD`, `RETURN_INCIDENT` | no |
| 2 | Ship | Deploy this Ship; it explores. If Bot has 5+ [Military] send an [Away Team] to a neutral Location. Otherwise gain a [Research]. | 1. Deploy this Ship and explore.<br>2. If the Bot's Military is 5 or more, send an Away Team to a neutral Location; otherwise gain 1 Research. | `DEPLOY`, `EXPLORE`, `SEND_AWAY_TEAM`, `GAIN_SPECIALTY` | no |
| 3 | Ally | Gain a Human > Person. Send an [Away Team] to a neutral Location. Log this card. | 1. Gain the most valuable Human; if none, the most valuable Person.<br>2. Send an Away Team to a neutral Location.<br>3. Log this card. | `GAIN_CARD`, `SEND_AWAY_TEAM`, `LOG` | no |
| 4 | Cargo | Gain 1 [Research] / [Military] (whichever is higher). | 1. Gain 1 in whichever of Research or Military is higher; ties go to Research. | `GAIN_SPECIALTY` | yes |
| 5 | Person | Log the top card of the Bot deck. Gain 1 [Research] / [Military] (whichever is lower). Send an [Away Team] to a neutral Location. Promote this card to Duty Officer. | 1. Log the top card of the Bot deck.<br>2. Gain 1 in whichever of Research or Military is lower.<br>3. Send an Away Team to a neutral Location.<br>4. Promote this card. | `LOG`, `GAIN_SPECIALTY`, `SEND_AWAY_TEAM`, `PROMOTE` | yes |
| 6 | Directive | Gain a [Research Focus] > Scientist / Telepath > Ally and gain an Incident. | 1. Gain the most valuable card with a Research Focus; else a Scientist or Telepath; else an Ally.<br>2. Gain an Incident, to the Bot Discard pile (REQ-SOLO-147). | `GAIN_CARD`, `TAKE_INCIDENT` | no |
| 7 | Encounter | Gain 1 [Research]. Discard the top card of the Supplement deck. | 1. Gain 1 Research.<br>2. Discard the top card of the Supplement deck. | `GAIN_SPECIALTY`, `DISCARD` | yes |
| 8 | Location | Discard the top 3 cards of the Bot deck. Gain 1 [Glory]. | 1. Discard the top 3 cards of the Bot deck.<br>2. Gain 1 Glory. | `DISCARD`, `GAIN_RESOURCE` | yes |

## SUITS WITH DUTY OFFICER

Image id: `soval-with-duty-officer`.

Used while the Bot has a Duty Officer. Flip back when it is dismissed or logged (REQ-SOLO-91 to REQ-SOLO-95).

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Log the top card of the Bot deck. Gain 1 [Research]. Gain 1 [Military]. Return this card. | 1. Log the top card of the Bot deck.<br>2. Gain 1 Research and 1 Military.<br>3. Return this card. | `LOG`, `GAIN_SPECIALTY`, `RETURN_INCIDENT` | yes |
| 2 | Ship | Deploy this Ship; it explores. Gain 1 [Military]. Send an [Away Team] to a neutral Location. | 1. Deploy and explore.<br>2. Gain 1 Military.<br>3. Send an Away Team to a neutral Location. | `DEPLOY`, `EXPLORE`, `GAIN_SPECIALTY`, `SEND_AWAY_TEAM` | no |
| 3 | Ally | Gain a Scientist / Telepath > Ship > Ally. If Duty Officer is not Vulcan, log Duty Officer. Log this card. | 1. Gain the most valuable Scientist or Telepath; else a Ship; else an Ally.<br>2. If the Duty Officer is not Vulcan, log it and flip SUITS.<br>3. Log this card. | `GAIN_CARD`, `LOG` | no |
| 4 | Cargo | Gain Scientist / Anomaly / Engineer > Ally, including from Junk. Dismiss Duty Officer. | 1. Gain the most valuable Scientist, Anomaly or Engineer from the Market or Junk; else an Ally.<br>2. Dismiss the Duty Officer and flip SUITS. | `GAIN_CARD`, `DISMISS` | no |
| 5 | Person | If Ship is in Bot Discard, put it on top of the Bot deck. Gain a [Research Focus] > [Military Focus] > [Influence Focus] > Ship and dismiss Duty Officer. | 1. If a Ship is in the Bot Discard pile, put the topmost one on top of the Bot deck.<br>2. Gain a card with Research Focus; else Military Focus; else Influence Focus; else a Ship.<br>3. Dismiss the Duty Officer and flip SUITS. | `PUT`, `GAIN_CARD`, `DISMISS` | no |
| 6 | Directive | Gain 1 [Research]. Gain 1 [Influence] / [Military] (whichever is lower). If Duty Officer is Vulcan, discard the top 2 cards of the Bot deck; otherwise gain 1 [Glory]. | 1. Gain 1 Research.<br>2. Gain 1 in whichever of Influence or Military is lower.<br>3. If the Duty Officer is Vulcan, discard the top 2 cards of the Bot deck; otherwise gain 1 Glory. | `GAIN_SPECIALTY`, `DISCARD`, `GAIN_RESOURCE` | yes |
| 7 | Encounter | Gain 1 [Research]. Gain 1 [Influence]. Resolve the top card of the Supplement deck. Log this card. | 1. Gain 1 Research and 1 Influence.<br>2. Resolve the top card of the Supplement deck.<br>3. Log this card. | `GAIN_SPECIALTY`, `RESOLVE_CARD`, `LOG` | no |
| 8 | Location | Gain 1 [Influence]. Gain a [Research Focus] > Starfleet > Cargo. Log Duty Officer. | 1. Gain 1 Influence.<br>2. Gain a card with a Research Focus icon; else a Starfleet; else a Cargo.<br>3. Log the Duty Officer and flip SUITS. | `GAIN_SPECIALTY`, `GAIN_CARD`, `LOG` | no |

## Five-Year Mission upgrades

Image id: `soval-five-year-mission-upgrades`. Used only in the solo campaign (REQ-CAMP-25 to REQ-CAMP-31).

### WIN

- **A. Common card types you can reinforce:** Telepath / [Research]
- **B. Alternative bonuses, pick 1:**
  - BOOST: Gain 1 [Research], 1 [Military], and 1 [Research]/[Military].
  - BOOST: Before drawing the starting hand, find a Person, except in your Reserve deck, and promote them to Duty Officer.

### LOSS

- **A. Common card types you can reinforce:** Vulcan / Scientist / Anomaly
- **B. Alternative bonuses, pick 1:**
  - BOOST: Gain 1 [Research]/[Military].
  - BOOST: After drawing the starting hand, find a Person in your Draw deck.

## Rulings and open questions

- The Location row with a Duty Officer gains a Research **Focus** card first: the icon on the card has the folded corner, and the solo example (p. 14) says no Market card had a Research Focus.

- The solo rulebook's full turn example (solo pp. 11–15) uses these rows and is the acceptance test for this file (REQ-SOLO in 22-solo-mode.md §13).
- "Take [Research] / [Influence] / [Military]" is read as taking a card with any of those Skill icons, most valuable first, matching the solo example where the Bot takes Vidiians.
- The Directive row says "gain an Incident"; Bot rows that gain an Incident put it in the Bot Discard pile (REQ-SOLO-147).
- The Soval Status card is removed when Soval is the Bot (REQ-SOLO-26).

## Tests

- Solo example step 3: Sub-Commander T'Pol matches Telepath, promotes, then continues to the Scientist row and takes Vidiians.
- Solo example step 4: Stel matches Attack with the Bot at 4 Military; the human removes an Away Team, the Bot cannot send one, so it gains 2 Military.
- Solo example step 6: Paan Mokar has no matching trait row and uses the Location row with a Duty Officer, gaining EVA Suit and logging T'Pol.
