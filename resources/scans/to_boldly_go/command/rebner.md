---
id: rebner-command
name: Rebner Automated Command cards
suit: Automated Command
deck: rebner
set: to_boldly_go
sides:
  - rebner-traits   # rebner-traits.jpg
  - rebner-no-duty-officer   # rebner-no-duty-officer.jpg
  - rebner-with-duty-officer   # rebner-with-duty-officer.jpg
  - rebner-five-year-mission-upgrades   # rebner-five-year-mission-upgrades.jpg
---

# Rebner Automated Command cards

The Bot playing Rebner's Crew deck resolves every card with these rows instead of the card's own text (REQ-SOLO-80 to REQ-SOLO-83). Each row becomes one function in `server/engine/bot/rebner.py`, following the Bot action rules in CLAUDE.md.

## How a card is resolved

1. If the card has the Surprise trait, resolve its SURPRISE operation and stop (REQ-SOLO-87).
2. Otherwise check the TRAITS rows from top to bottom. The first row with a trait the card has is used. A Wildcard card matches the first trait row (REQ-SOLO-82).
3. If no trait row matches, use the row for the card's suit on whichever SUITS side is face up: WITH NO DUTY OFFICER, or WITH DUTY OFFICER.
4. "Continue resolution" stops the current row and finds the next matching row, trait rows first, then suits (REQ-SOLO-120).
5. A Location still in the Staging Area afterwards moves to the Bot's Control Area (REQ-SOLO-89).

Text shown **in bold** is resolved by the human player. On the card, bold red text is an attack, which the human may cancel; bold black text affects the human without attacking. Rows with an attack list the `ATTACK` action (REQ-SOLO-180 to REQ-SOLO-185).

## Special rule

Research and Influence multipliers are always 0 for the Rebner Bot (REQ-CD-REB-02).

## TRAITS

Image id: `rebner-traits`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Surprise | Resolve this card's Surprise operation. | 1. Resolve the card's SURPRISE (Bot only) operation instead of any row. |  | yes |
| 2 | Helmet | If this card is Big Enough Helmet, take top Encounter and log this card. Otherwise, gain the most valuable card in the Market and discard the top 2 cards of the Bot deck. | 1. If this card is Big Enough Helmet, take top Encounter and log this card..<br>2. Otherwise, gain the most valuable card in the Market and discard the top 2 cards of the Bot deck. | `TAKE_ENCOUNTER`, `LOG`, `GAIN_CARD`, `DISCARD` | no |
| 3 | Weapon | If Bot has 6+ [Military], log this card and **you take an Incident**. Otherwise, gain 1 [Military] and send an [Away Team] to a neutral Location. | 1. If Bot has 6+ [Military], log this card and you take an Incident..<br>2. Otherwise, gain 1 [Military] and send an [Away Team] to a neutral Location. | `LOG`, `ATTACK`, `TAKE_INCIDENT`, `GAIN_SPECIALTY`, `SEND_AWAY_TEAM` | no |
| 4 | Attack | If able to do both, log a Weapon from Bot Discard pile, and **you log a Ship either from your hand, Discard pile, or in play**. Otherwise, **you discard a card**. If this card is a Ship, deploy it; it engages. If this card is a Person, promote it to Duty Officer. | 1. If able to do both, log a Weapon from Bot Discard pile, and you log a Ship either from your hand, Discard pile, or in play..<br>2. Otherwise, you discard a card..<br>3. If this card is a Ship, deploy it; it engages..<br>4. If this card is a Person, promote it to Duty Officer. | `LOG`, `ATTACK`, `DISCARD`, `DEPLOY`, `ENGAGE`, `PROMOTE` | no |
| 5 | Engineer | Junk the most valuable card in the Market (ignoring any with tokens). Discard the top card of the Supplement deck. Gain 1 [Military]. If this card is a Person, promote it to Duty Officer. | 1. Junk the most valuable card in the Market (ignoring any with tokens)..<br>2. Discard the top card of the Supplement deck..<br>3. Gain 1 [Military]..<br>4. If this card is a Person, promote it to Duty Officer. | `JUNK`, `DISCARD`, `GAIN_SPECIALTY`, `PROMOTE` | no |
| 6 | Scientist / Communication | Gain 1 [Military]. If this card is a Ship, deploy this Ship; it explores. Otherwise, log the top card of the Bot deck, gain 1 [Glory], and if able, gain a [Military Focus] > Cargo, including from the Junk. | 1. Gain 1 [Military]..<br>2. If this card is a Ship, deploy this Ship; it explores..<br>3. Otherwise, log the top card of the Bot deck, gain 1 [Glory], and if able, gain a [Military Focus] > Cargo, including from the Junk. | `GAIN_SPECIALTY`, `DEPLOY`, `EXPLORE`, `LOG`, `GAIN_RESOURCE`, `GAIN_CARD` | no |

## SUITS WITH NO DUTY OFFICER

Image id: `rebner-no-duty-officer`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Junk the most valuable card in the Market (ignoring any with tokens). If able, gain a [Military Focus]. Otherwise, gain 2 [Military]. Return this card. | 1. Junk the most valuable card in the Market (ignoring any with tokens)..<br>2. If able, gain a [Military Focus]..<br>3. Otherwise, gain 2 [Military]..<br>4. Return this card. | `JUNK`, `GAIN_CARD`, `GAIN_SPECIALTY`, `RETURN_INCIDENT` | no |
| 2 | Ship | Deploy this Ship; it explores. If a Helmet is in Bot Discard pile: If able, gain a Helmet / Cargo / [Military Focus] from the Junk. Otherwise, send an [Away Team] to a neutral Location. | 1. Deploy this Ship; it explores..<br>2. If a Helmet is in Bot Discard pile: If able, gain a Helmet / Cargo / [Military Focus] from the Junk..<br>3. Otherwise, send an [Away Team] to a neutral Location. | `DEPLOY`, `EXPLORE`, `GAIN_CARD`, `SEND_AWAY_TEAM` | no |
| 3 | Ally | Discard the top card of the Supplement deck. Gain 2 [Military]. If able, gain a [Military Focus] from the Junk. **You take an Incident.** Log this card. | 1. Discard the top card of the Supplement deck..<br>2. Gain 2 [Military]..<br>3. If able, gain a [Military Focus] from the Junk..<br>4. You take an Incident..<br>5. Log this card. | `DISCARD`, `GAIN_SPECIALTY`, `GAIN_CARD`, `ATTACK`, `TAKE_INCIDENT`, `LOG` | no |
| 4 | Cargo | If a Helmet is in Bot Discard pile, take an Incident and gain a Ship / Ally. Otherwise, discard the top 2 cards of the Bot deck, then if able, gain a [Military Focus] > Person > Cargo from the Junk. | 1. If a Helmet is in Bot Discard pile, take an Incident and gain a Ship / Ally..<br>2. Otherwise, discard the top 2 cards of the Bot deck, then if able, gain a [Military Focus] > Person > Cargo from the Junk. | `TAKE_INCIDENT`, `GAIN_CARD`, `DISCARD` | no |
| 5 | Person | Gain a Weapon > Ship. Promote this card to Duty Officer. | 1. Gain a Weapon > Ship..<br>2. Promote this card to Duty Officer. | `GAIN_CARD`, `PROMOTE` | no |
| 6 | Directive | Junk the most valuable card in the Market (ignoring any with tokens). Discard the top 3 cards of the Bot deck. If able, promote a Person from Bot Discard pile to Duty Officer. Otherwise, send an [Away Team] to a neutral Location. | 1. Junk the most valuable card in the Market (ignoring any with tokens)..<br>2. Discard the top 3 cards of the Bot deck..<br>3. If able, promote a Person from Bot Discard pile to Duty Officer..<br>4. Otherwise, send an [Away Team] to a neutral Location. | `JUNK`, `DISCARD`, `PROMOTE`, `SEND_AWAY_TEAM` | no |
| 7 | Encounter | Discard the top 2 cards of the Bot deck. Gain a [Military Focus] > Attack > Weapon > Ship. Gain 1 [Glory]. Log this card. | 1. Discard the top 2 cards of the Bot deck..<br>2. Gain a [Military Focus] > Attack > Weapon > Ship..<br>3. Gain 1 [Glory]..<br>4. Log this card. | `DISCARD`, `GAIN_CARD`, `GAIN_RESOURCE`, `LOG` | no |
| 8 | Location | If able, gain an Engineer / Communication / Scientist. Otherwise, gain a Weapon / Attack > Person from the Junk. | 1. If able, gain an Engineer / Communication / Scientist..<br>2. Otherwise, gain a Weapon / Attack > Person from the Junk. | `GAIN_CARD` | no |

## SUITS WITH DUTY OFFICER

Image id: `rebner-with-duty-officer`.

Used while the Bot has a Duty Officer. Flip back when it is dismissed or logged (REQ-SOLO-91 to REQ-SOLO-95).

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Gain 1 [Military]. Send an [Away Team] to a neutral Location. Return this card. | 1. Gain 1 [Military]..<br>2. Send an [Away Team] to a neutral Location..<br>3. Return this card. | `GAIN_SPECIALTY`, `SEND_AWAY_TEAM`, `RETURN_INCIDENT` | yes |
| 2 | Ship | Deploy this Ship; it engages. If a Helmet is in Bot Discard pile, send an [Away Team] to a neutral Location. Otherwise, discard the top 2 cards of the Bot deck. | 1. Deploy this Ship; it engages..<br>2. If a Helmet is in Bot Discard pile, send an [Away Team] to a neutral Location..<br>3. Otherwise, discard the top 2 cards of the Bot deck. | `DEPLOY`, `ENGAGE`, `SEND_AWAY_TEAM`, `DISCARD` | no |
| 3 | Ally | Take an Incident. Gain 1 [Military]. If able, gain a [Military Focus]. Otherwise, gain a Cargo and log Duty Officer. Log this card. | 1. Take an Incident..<br>2. Gain 1 [Military]..<br>3. If able, gain a [Military Focus]..<br>4. Otherwise, gain a Cargo and log Duty Officer..<br>5. Log this card. | `TAKE_INCIDENT`, `GAIN_SPECIALTY`, `GAIN_CARD`, `LOG` | no |
| 4 | Cargo | Gain a [Military Focus] > Person. Gain 1 [Military] and **you remove an [Away Team] from a neutral Location** where the Bot has 1+ token. Send an [Away Team] to a neutral Location. Dismiss Duty Officer. | 1. Gain a [Military Focus] > Person..<br>2. Gain 1 [Military] and you remove an [Away Team] from a neutral Location where the Bot has 1+ token..<br>3. Send an [Away Team] to a neutral Location..<br>4. Dismiss Duty Officer. | `GAIN_CARD`, `GAIN_SPECIALTY`, `ATTACK`, `REMOVE_AWAY_TEAM`, `SEND_AWAY_TEAM`, `DISMISS` | no |
| 5 | Person | If the top card of the Bot deck is a Helmet, discard it and send an [Away Team] to a neutral Location. Otherwise, log it, gain 1 [Military], and gain an Communication > Scientist > Ally / Ship, including from the Junk. | 1. If the top card of the Bot deck is a Helmet, discard it and send an [Away Team] to a neutral Location..<br>2. Otherwise, log it, gain 1 [Military], and gain an Communication > Scientist > Ally / Ship, including from the Junk. | `PEEK`, `DISCARD`, `SEND_AWAY_TEAM`, `LOG`, `GAIN_SPECIALTY`, `GAIN_CARD` | no |
| 6 | Directive | Junk the most valuable card in the Market (ignoring any with tokens). Discard the top 2 cards of the Bot deck. If a Helmet is in Bot Discard pile, gain a Cargo / Ship. Otherwise, send an [Away Team] to a neutral Location and gain 1 [Military]. | 1. Junk the most valuable card in the Market (ignoring any with tokens)..<br>2. Discard the top 2 cards of the Bot deck..<br>3. If a Helmet is in Bot Discard pile, gain a Cargo / Ship..<br>4. Otherwise, send an [Away Team] to a neutral Location and gain 1 [Military]. | `JUNK`, `DISCARD`, `GAIN_CARD`, `SEND_AWAY_TEAM`, `GAIN_SPECIALTY` | no |
| 7 | Encounter | Gain 1 [Glory]. Gain an Engineer / Communication / Scientist > Person, including from the Junk. Log this card. | 1. Gain 1 [Glory]..<br>2. Gain an Engineer / Communication / Scientist > Person, including from the Junk..<br>3. Log this card. | `GAIN_RESOURCE`, `GAIN_CARD`, `LOG` | no |
| 8 | Location | If a Helmet is in Bot Discard pile, gain 1 [Military] and discard the top card of the Supplement deck. Otherwise, dismiss Duty Officer, then resolve the top card of the Bot deck. | 1. If a Helmet is in Bot Discard pile, gain 1 [Military] and discard the top card of the Supplement deck..<br>2. Otherwise, dismiss Duty Officer, then resolve the top card of the Bot deck. | `GAIN_SPECIALTY`, `DISCARD`, `DISMISS`, `RESOLVE_CARD` | no |

## Five-Year Mission upgrades

Image id: `rebner-five-year-mission-upgrades`. Used only in the solo campaign (REQ-CAMP-25 to REQ-CAMP-31).

### WIN

- **A. Common card types you can reinforce:** Cargo (except Helmet)
- **B. Alternative bonuses, pick 1:**
  - BOOST: After drawing the starting hand, discard up to 3 cards from your hand, then draw the same number of cards.
  - BOOST: After drawing the starting hand, gain a card from the top of the deck or from the Junk.

### LOSS

- **A. Common card types you can reinforce:** Business / Shady / Attack
- **B. Alternative bonuses, pick 1:**
  - BOOST: After drawing the starting hand, take an Incident to scan 1 of Cargo.
  - BOOST: Gain 1 [Latinum].

## Rulings and open questions

- The "[Military Focus]" icons on these rows are read as Focus icons (folded corner). Verify against the printed card.
- The Bot's hand-size rule does not apply; the Bot has no hand.

## Tests

- Given the Bot has 6 Military, when it resolves a Weapon, it logs the card and the human takes an Incident.
