---
id: archer-command
name: Archer Automated Command cards
suit: Automated Command
deck: archer
set: to_boldly_go
sides:
  - archer-traits   # archer-traits.jpg
  - archer-no-duty-officer   # archer-no-duty-officer.jpg
  - archer-with-duty-officer   # archer-with-duty-officer.jpg
  - archer-five-year-mission-upgrades   # archer-five-year-mission-upgrades.jpg
---

# Archer Automated Command cards

The Bot playing Archer's Crew deck resolves every card with these rows instead of the card's own text (REQ-SOLO-80 to REQ-SOLO-83). Each row becomes one function in `server/engine/bot/archer.py`, following the Bot action rules in CLAUDE.md.

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

Image id: `archer-traits`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Surprise | Resolve this card's Surprise operation. | 1. Resolve the card's SURPRISE (Bot only) operation instead of any row. |  | yes |
| 2 | Time Travel | Gain 1 [Research], 1 [Influence], 1 [Military]. Continue resolution. | 1. Gain 1 [Research], 1 [Influence], 1 [Military]..<br>2. Continue resolution. | `GAIN_SPECIALTY`, `CONTINUE_RESOLUTION` | yes |
| 3 | NX-01 | If this card is a Person, gain a [Research Focus]/[Influence Focus]/[Military Focus] > Cargo. Otherwise, if this card is a Cargo, gain an Incident and resolve the top card of the Supplement deck. Otherwise, continue resolution. | 1. If this card is a Person, gain a [Research Focus]/[Influence Focus]/[Military Focus] > Cargo..<br>2. Otherwise, if this card is a Cargo, gain an Incident and resolve the top card of the Supplement deck..<br>3. Otherwise, continue resolution. | `GAIN_CARD`, `TAKE_INCIDENT`, `RESOLVE_CARD`, `CONTINUE_RESOLUTION` | no |
| 4 | Vulcan / Andorian / Tellarite | Discard the top card of the Supplement deck. If able, gain Andorian / Vulcan / Tellarite. Otherwise add an [Away Team] token from the supply to the Bot Captain card (max 6 [Away Team] total), and send it to a neutral Location. Continue resolution. | 1. Discard the top card of the Supplement deck..<br>2. If able, gain Andorian / Vulcan / Tellarite..<br>3. Otherwise add an [Away Team] token from the supply to the Bot Captain card (max 6 [Away Team] total), and send it to a neutral Location..<br>4. Continue resolution. | `DISCARD`, `GAIN_CARD`, `ADD_AWAY_TEAM`, `SEND_AWAY_TEAM`, `CONTINUE_RESOLUTION` | no |
| 5 | Xindi | Gain 1 [Influence]. If Bot has 7 or fewer [Influence], gain (if able) Xindi > Time Travel > Andorian / Tellarite / Vulcan, including from the Junk. Otherwise, gain top Encounter and log this card, and **you exhaust a controlled Location**, and if you have a Xindi in play, both the bot and **you take an Incident**. | 1. Gain 1 [Influence]..<br>2. If Bot has 7 or fewer [Influence], gain (if able) Xindi > Time Travel > Andorian / Tellarite / Vulcan, including from the Junk..<br>3. Otherwise, gain top Encounter and log this card, and you exhaust a controlled Location, and if you have a Xindi in play, both the bot and you take an Incident. | `GAIN_SPECIALTY`, `GAIN_CARD`, `TAKE_ENCOUNTER`, `LOG`, `ATTACK`, `EXHAUST`, `TAKE_INCIDENT` | no |
| 6 | Attack | Send an [Away Team] to a neutral Location. If able, **you remove all your [Away Team] from a neutral Location** where the bot has a Ship then log this card. Otherwise, log a non-NX-01 card from the bot Discard pile and gain all resources from a card in the Market. | 1. Send an [Away Team] to a neutral Location..<br>2. If able, you remove all your [Away Team] from a neutral Location where the bot has a Ship then log this card..<br>3. Otherwise, log a non-NX-01 card from the bot Discard pile and gain all resources from a card in the Market. | `SEND_AWAY_TEAM`, `ATTACK`, `REMOVE_AWAY_TEAM`, `LOG`, `GAIN_RESOURCE` | no |

## SUITS WITH NO DUTY OFFICER

Image id: `archer-no-duty-officer`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Log the top card of the Bot deck. Gain 1 [Research]. Return this card. | 1. Log the top card of the Bot deck..<br>2. Gain 1 [Research]..<br>3. Return this card. | `LOG`, `GAIN_SPECIALTY`, `RETURN_INCIDENT` | yes |
| 2 | Ship | Discard the top 2 cards of the Bot deck. Deploy this Ship; it explores. If able, send an [Away Team] to a neutral Xindi / Tellarite; otherwise gain 1 [Glory]. | 1. Discard the top 2 cards of the Bot deck..<br>2. Deploy this Ship; it explores..<br>3. If able, send an [Away Team] to a neutral Xindi / Tellarite; otherwise gain 1 [Glory]. | `DISCARD`, `DEPLOY`, `EXPLORE`, `SEND_AWAY_TEAM`, `GAIN_RESOURCE` | no |
| 3 | Ally | Gain Andorian / Vulcan > Alien / Ambassador > Person. Log this card. | 1. Gain Andorian / Vulcan > Alien / Ambassador > Person..<br>2. Log this card. | `GAIN_CARD`, `LOG` | no |
| 4 | Cargo | Discard the top 2 cards of the Bot deck. Resolve an NX-01 from Bot Discard if able; otherwise gain a Ship and gain an Incident. | 1. Discard the top 2 cards of the Bot deck..<br>2. Resolve an NX-01 from Bot Discard if able; otherwise gain a Ship and gain an Incident. | `DISCARD`, `RESOLVE_CARD`, `GAIN_CARD`, `TAKE_INCIDENT` | no |
| 5 | Person | Gain Xindi / Andorian > Cargo. Promote this card to Duty Officer. | 1. Gain Xindi / Andorian > Cargo..<br>2. Promote this card to Duty Officer. | `GAIN_CARD`, `PROMOTE` | no |
| 6 | Directive | Discard the top card of the Bot deck. Gain NX-01 if able; otherwise twice: gain 1 [Research] / [Influence] / [Military] (whichever is lower). Promote a Person with NX-01 from the Bot Discard pile to Duty Officer, if able. | 1. Discard the top card of the Bot deck..<br>2. Gain NX-01 if able; otherwise twice: gain 1 [Research] / [Influence] / [Military] (whichever is lower)..<br>3. Promote a Person with NX-01 from the Bot Discard pile to Duty Officer, if able. | `DISCARD`, `GAIN_CARD`, `GAIN_SPECIALTY`, `PROMOTE` | no |
| 7 | Encounter | Discard the top card of the Supplement deck. Log this card. | 1. Discard the top card of the Supplement deck..<br>2. Log this card. | `DISCARD`, `LOG` | yes |
| 8 | Location | Discard the top 2 cards of the Bot deck. Gain a Person. Gain 3 [Glory] from the supply. | 1. Discard the top 2 cards of the Bot deck..<br>2. Gain a Person..<br>3. Gain 3 [Glory] from the supply. | `DISCARD`, `GAIN_CARD`, `GAIN_RESOURCE` | no |

## SUITS WITH DUTY OFFICER

Image id: `archer-with-duty-officer`.

Used while the Bot has a Duty Officer. Flip back when it is dismissed or logged (REQ-SOLO-91 to REQ-SOLO-95).

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Log the top card of the Bot deck. Gain 1 [Research]. Return this card. | 1. Log the top card of the Bot deck..<br>2. Gain 1 [Research]..<br>3. Return this card. | `LOG`, `GAIN_SPECIALTY`, `RETURN_INCIDENT` | yes |
| 2 | Ship | Deploy this Ship; it engages. Send an [Away Team] to a neutral Xindi / Tellarite > Location. Gain 1 [Military]. Dismiss Duty Officer. | 1. Deploy this Ship; it engages..<br>2. Send an [Away Team] to a neutral Xindi / Tellarite > Location..<br>3. Gain 1 [Military]..<br>4. Dismiss Duty Officer. | `DEPLOY`, `ENGAGE`, `SEND_AWAY_TEAM`, `GAIN_SPECIALTY`, `DISMISS` | no |
| 3 | Ally | Gain Xindi > Tellarite > Ship. Log this card. | 1. Gain Xindi > Tellarite > Ship..<br>2. Log this card. | `GAIN_CARD`, `LOG` | no |
| 4 | Cargo | Log the top card of the Bot deck. Send an [Away Team] to a neutral Xindi / Tellarite > Location. Dismiss Duty Officer. Log this card. | 1. Log the top card of the Bot deck..<br>2. Send an [Away Team] to a neutral Xindi / Tellarite > Location..<br>3. Dismiss Duty Officer..<br>4. Log this card. | `LOG`, `SEND_AWAY_TEAM`, `DISMISS` | yes |
| 5 | Person | Resolve a Directive from the Bot Discard pile if able; otherwise gain 1 [Glory]. Dismiss Duty Officer. | 1. Resolve a Directive from the Bot Discard pile if able; otherwise gain 1 [Glory]..<br>2. Dismiss Duty Officer. | `RESOLVE_CARD`, `GAIN_RESOURCE`, `DISMISS` | no |
| 6 | Directive | If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter, then log this card. Otherwise, gain NX-01 > Ally / Ship. If a Ship was gained, dismiss Duty Officer; otherwise send [Away Team] to a neutral Location. | 1. If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter, then log this card..<br>2. Otherwise, gain NX-01 > Ally / Ship..<br>3. If a Ship was gained, dismiss Duty Officer; otherwise send [Away Team] to a neutral Location. | `LOG`, `REMOVE_AWAY_TEAM`, `TAKE_ENCOUNTER`, `GAIN_CARD`, `DISMISS`, `SEND_AWAY_TEAM` | no |
| 7 | Encounter | Resolve the top card of the Supplement deck. Log this card. | 1. Resolve the top card of the Supplement deck..<br>2. Log this card. | `RESOLVE_CARD`, `LOG` | no |
| 8 | Location | Discard the top card of the Supplement deck. Log the top 2 cards of the Bot deck. Gain 1 [Glory] (from the Stardate card), and another 2 [Glory] from the supply. Log Duty Officer. | 1. Discard the top card of the Supplement deck..<br>2. Log the top 2 cards of the Bot deck..<br>3. Gain 1 [Glory] (from the Stardate card), and another 2 [Glory] from the supply..<br>4. Log Duty Officer. | `DISCARD`, `LOG`, `GAIN_RESOURCE` | yes |

## Five-Year Mission upgrades

Image id: `archer-five-year-mission-upgrades`. Used only in the solo campaign (REQ-CAMP-25 to REQ-CAMP-31).

### WIN

- **A. Common card types you can reinforce:** NX-01 / Andorian / Tellarite
- **B. Alternative bonuses, pick 1:**
  - BOOST: After drawing the starting hand, enlist a Reserve.
  - BOOST: After drawing the starting hand, spend 1 [Dilithium] to scan for NX-01.

### LOSS

- **A. Common card types you can reinforce:** Xindi / Vulcan / Ally
- **B. Alternative bonuses, pick 1:**
  - BOOST: After drawing the starting hand, spend 1 [Glory] to scan for NX-01.
  - REINFORCE: A non-Incident card from your Reserve deck.

## Rulings and open questions

- The Vulcan / Andorian / Tellarite row adds Away Teams to the Bot Captain from the supply, up to 6; using ADD_AWAY_TEAM.
- In the Xindi row, the bold red parts are attacks: the human exhausts a controlled Location and takes an Incident.

## Tests

- Given the Bot resolves a Time Travel card, it gains 1 on each track and continues to the next matching row.
