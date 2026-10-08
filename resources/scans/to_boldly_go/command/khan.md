---
id: khan-command
name: Khan Automated Command cards
suit: Automated Command
deck: khan
set: to_boldly_go
sides:
  - khan-traits   # khan-traits.jpg
  - khan-in-exile-traits   # khan-in-exile-traits.jpg
  - khan-no-duty-officer   # khan-no-duty-officer.jpg
  - khan-with-duty-officer   # khan-with-duty-officer.jpg
  - khan-five-year-mission-upgrades   # khan-five-year-mission-upgrades.jpg
---

# Khan Automated Command cards

The Bot playing Khan's Crew deck resolves every card with these rows instead of the card's own text (REQ-SOLO-80 to REQ-SOLO-83). Each row becomes one function in `server/engine/bot/khan.py`, following the Bot action rules in CLAUDE.md.

## How a card is resolved

1. If the card has the Surprise trait, resolve its SURPRISE operation and stop (REQ-SOLO-87).
2. Otherwise check the TRAITS rows from top to bottom. The first row with a trait the card has is used. A Wildcard card matches the first trait row (REQ-SOLO-82).
3. If no trait row matches, use the row for the card's suit on whichever SUITS side is face up: WITH NO DUTY OFFICER, or WITH DUTY OFFICER.
4. "Continue resolution" stops the current row and finds the next matching row, trait rows first, then suits (REQ-SOLO-120).
5. A Location still in the Staging Area afterwards moves to the Bot's Control Area (REQ-SOLO-89).

Text shown **in bold** is resolved by the human player. On the card, bold red text is an attack, which the human may cancel; bold black text affects the human without attacking. Rows with an attack list the `ATTACK` action (REQ-SOLO-180 to REQ-SOLO-185).

## Special rule

At the end of the game the bot scores 3 [VP] for each marked trait, and it considers each **unmarked** card's value 3 higher when gaining cards. Each [Research]/[Influence]/[Military] scores (and is valued for it at) 3.

Solo setup for the Khan Bot (REQ-CD-KHN-11): remove Ceti Alpha V and VI, start with the KHAN IN EXILE card, and switch to the regular TRAITS and SUITS cards when that card says so. "Unmarked" in a row means a card or Location with a trait not yet marked on the board.

## KHAN IN EXILE TRAITS

Image id: `khan-in-exile-traits`.

Used first. Its rules:

- If a Location is played during its Action Step, it is **not** placed into the bot's Control Area.
- Whenever a card is drawn or discarded from the Supplement deck, the bot gains 1 [Dilithium].
- At the end of its turn, the bot gains 1 [Dilithium]. Then, if it has 5+ [Dilithium], it spends them all, gains the top Encounter, and replaces this card with the regular Automated Command cards.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Surprise | Resolve this card's Surprise operation. | 1. Resolve the card's SURPRISE (Bot only) operation instead of any row. |  | yes |
| 2 | Augment | Send an [Away Team] to a neutral unmarked > Augment / Scientist > Location. Take an Incident to gain a Person. | 1. Send an [Away Team] to a neutral unmarked > Augment / Scientist > Location..<br>2. Take an Incident to gain a Person. | `SEND_AWAY_TEAM`, `TAKE_INCIDENT`, `GAIN_CARD` | no |
| 3 | Incident | Discard the top card of the Bot deck. If the discarded card shares a non-Human trait with your Captain, gain 1 [Glory]. Return this card. | 1. Discard the top card of the Bot deck..<br>2. If the discarded card shares a non-Human trait with your Captain, gain 1 [Glory]..<br>3. Return this card. | `DISCARD`, `GAIN_RESOURCE`, `RETURN_INCIDENT` | yes |
| 4 | Ship | Junk the most valuable card in the Market (ignoring any with tokens). Send an [Away Team] to a neutral unmarked > Location. | 1. Junk the most valuable card in the Market (ignoring any with tokens)..<br>2. Send an [Away Team] to a neutral unmarked > Location. | `JUNK`, `SEND_AWAY_TEAM` | no |
| 5 | Directive | Junk the most valuable card in the Market (ignoring any with tokens). Gain an unmarked > Person / Cargo / Ship / Ally from the Junk. | 1. Junk the most valuable card in the Market (ignoring any with tokens)..<br>2. Gain an unmarked > Person / Cargo / Ship / Ally from the Junk. | `JUNK`, `GAIN_CARD` | no |
| 6 | Person / Cargo / Ally / Location | Discard the top card of the Bot deck. If this card is a Location taken during the Control Step, gain an Incident, and spend 1 [Dilithium], if able. If this card is a Person, gain 1 [Glory] from the supply. | 1. Discard the top card of the Bot deck..<br>2. If this card is a Location taken during the Control Step, gain an Incident, and spend 1 [Dilithium], if able..<br>3. If this card is a Person, gain 1 [Glory] from the supply. | `DISCARD`, `TAKE_INCIDENT`, `SPEND`, `GAIN_RESOURCE` | no |

## TRAITS

Image id: `khan-traits`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Surprise | Resolve this card's Surprise operation. | 1. Resolve the card's SURPRISE (Bot only) operation instead of any row. |  | yes |
| 2 | Mind Control | **You dismiss a Duty Officer, if able**, otherwise gain 2 [Glory]. Continue resolution. | 1. You dismiss a Duty Officer, if able, otherwise gain 2 [Glory]..<br>2. Continue resolution. | `ATTACK`, `DISMISS`, `GAIN_RESOURCE`, `CONTINUE_RESOLUTION` | no |
| 3 | Augment / Ops | Send an [Away Team] to a neutral unmarked > Augment / Scientist > Location. If this card is a Person, take an Incident and take a Person; otherwise discard the top card of the Supplement deck. | 1. Send an [Away Team] to a neutral unmarked > Augment / Scientist > Location..<br>2. If this card is a Person, take an Incident and take a Person; otherwise discard the top card of the Supplement deck. | `SEND_AWAY_TEAM`, `TAKE_INCIDENT`, `GAIN_CARD`, `DISCARD` | no |
| 4 | Creature / Scientist | Return an Incident from Bot Discard pile, if able. Send 2 [Away Team] to a neutral Location, ignoring any opponent Ship. Log this card. | 1. Return an Incident from Bot Discard pile, if able..<br>2. Send 2 [Away Team] to a neutral Location, ignoring any opponent Ship..<br>3. Log this card. | `RETURN_INCIDENT`, `SEND_AWAY_TEAM`, `LOG` | yes |
| 5 | Attack | Mark a trait. **You take an Incident from Bot Discard pile, if able.** Otherwise, **you find any card, and log the found card.** If this card is Revenge is a dish best served cold, **you log this card**; otherwise the bot logs this card. | 1. Mark a trait..<br>2. You take an Incident from Bot Discard pile, if able..<br>3. Otherwise, you find any card, and log the found card..<br>4. If this card is Revenge is a dish best served cold, you log this card; otherwise the bot logs this card. | `MARK_TRAIT`, `ATTACK`, `TAKE_INCIDENT`, `FIND`, `LOG` | no |

## SUITS WITH NO DUTY OFFICER

Image id: `khan-no-duty-officer`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Discard the top card of the Bot deck. If the discarded card shares a non-Human trait with your Captain, gain 1 [Glory]. Return this card. | 1. Discard the top card of the Bot deck..<br>2. If the discarded card shares a non-Human trait with your Captain, gain 1 [Glory]..<br>3. Return this card. | `DISCARD`, `GAIN_RESOURCE`, `RETURN_INCIDENT` | yes |
| 2 | Ship | Deploy this ship; it engages. | 1. Deploy this ship; it engages. | `DEPLOY`, `ENGAGE` | no |
| 3 | Ally | Take a Spy / Cloak / Synthetic if able; otherwise gain a Person / Ship. Log this card. | 1. Take a Spy / Cloak / Synthetic if able; otherwise gain a Person / Ship..<br>2. Log this card. | `GAIN_CARD`, `LOG` | no |
| 4 | Cargo | Gain a Person from the top of the deck. | 1. Gain a Person from the top of the deck. | `GAIN_CARD` | no |
| 5 | Person | Gain 1 [Glory]. Gain an Incident. Promote this card to Duty Officer. | 1. Gain 1 [Glory]..<br>2. Gain an Incident..<br>3. Promote this card to Duty Officer. | `GAIN_RESOURCE`, `TAKE_INCIDENT`, `PROMOTE` | no |
| 6 | Directive | Junk the most valuable card in the Market (ignoring any with tokens). Gain an Ally > Ship from the Junk. | 1. Junk the most valuable card in the Market (ignoring any with tokens)..<br>2. Gain an Ally > Ship from the Junk. | `JUNK`, `GAIN_CARD` | no |
| 7 | Encounter | Resolve the top card of the Supplement deck. | 1. Resolve the top card of the Supplement deck. | `RESOLVE_CARD` | no |
| 8 | Location | Discard the top 2 cards of the Bot deck. Gain a Ship. | 1. Discard the top 2 cards of the Bot deck..<br>2. Gain a Ship. | `DISCARD`, `GAIN_CARD` | no |

## SUITS WITH DUTY OFFICER

Image id: `khan-with-duty-officer`.

Used while the Bot has a Duty Officer. Flip back when it is dismissed or logged (REQ-SOLO-91 to REQ-SOLO-95).

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Discard the top card of the Bot deck. If the discarded card shares a non-Human trait with your Captain, gain 1 [Glory]. **You take this card.** | 1. Discard the top card of the Bot deck..<br>2. If the discarded card shares a non-Human trait with your Captain, gain 1 [Glory]..<br>3. You take this card. | `DISCARD`, `GAIN_RESOURCE`, `ATTACK`, `GIVE`, `RETURN_INCIDENT` | no |
| 2 | Ship | Deploy this ship; it engages. Send an [Away Team] to a neutral Location. | 1. Deploy this ship; it engages..<br>2. Send an [Away Team] to a neutral Location. | `DEPLOY`, `ENGAGE`, `SEND_AWAY_TEAM` | no |
| 3 | Ally | Gain a Cargo > Ally > Person. Log Duty Officer. Log this card. | 1. Gain a Cargo > Ally > Person..<br>2. Log Duty Officer..<br>3. Log this card. | `GAIN_CARD`, `LOG` | no |
| 4 | Cargo | Gain a Ally > Person / Ship. Log Duty Officer. | 1. Gain a Ally > Person / Ship..<br>2. Log Duty Officer. | `GAIN_CARD`, `LOG` | no |
| 5 | Person | Put an Augment from Bot Discard pile on top of the Bot deck, if able. Dismiss Duty Officer. | 1. Put an Augment from Bot Discard pile on top of the Bot deck, if able..<br>2. Dismiss Duty Officer. | `PUT`, `DISMISS` | yes |
| 6 | Directive | Junk the most valuable card in the Market (ignoring any with tokens). Gain a Person / Cargo / Ally, including from the Junk. | 1. Junk the most valuable card in the Market (ignoring any with tokens)..<br>2. Gain a Person / Cargo / Ally, including from the Junk. | `JUNK`, `GAIN_CARD` | no |
| 7 | Encounter | If 8 or more traits are marked, gain the highest value card of the top 3 Encounter and destroy the other two, then log the gained card and this card. Otherwise, resolve the top card of the Supplement deck. | 1. If 8 or more traits are marked, gain the highest value card of the top 3 Encounter and destroy the other two, then log the gained card and this card..<br>2. Otherwise, resolve the top card of the Supplement deck. | `TAKE_ENCOUNTER`, `DESTROY`, `LOG`, `RESOLVE_CARD` | no |
| 8 | Location | Discard the top card of the Supplement deck. Log Duty Officer. | 1. Discard the top card of the Supplement deck..<br>2. Log Duty Officer. | `DISCARD`, `LOG` | yes |

## Five-Year Mission upgrades

Image id: `khan-five-year-mission-upgrades`. Used only in the solo campaign (REQ-CAMP-25 to REQ-CAMP-31).

### WIN

- **A. Common card types you can reinforce:** Augment / Attack
- **B. Alternative bonuses, pick 1:**
  - BOOST: Before drawing the starting hand, spend 1 [Latinum] to scan for an Augment or a Creature or a Scientist.
  - ATTACK BOOST: Before drawing the starting hand, find an Incident, except in your Reserve deck, and give it to your opponent.

### LOSS

- **A. Common card types you can reinforce:** Person
- **B. Alternative bonuses, pick 1:**
  - BOOST: Before drawing the starting hand, spend 1 [Latinum] to scan for an Augment.
  - ATTACK BOOST: After drawing the starting hand, draw a card and your opponent takes an Incident.

## Rulings and open questions

- "Your Captain" in the Incident rows means the human's Captain.
- The Incident row with a Duty Officer gives the Incident to the human ("you take this card"), an attack. If you cancel it, the Incident is returned to the Incident deck (KW-GIVE-04).
- The Khan Bot never flips its Captain (REQ-CD-KHN-11).
- The Bot marks a trait whenever it gains, takes or takes control of a card, Incidents and Encounters included, and for the Encounter gained when it leaves exile. For an Opponent's Captain entry it uses the first fitting trait in the printed order of your Captain's traits.
- The 3 extra value for an unmarked card applies to every Bot choice by value, not only to gains.
- KHAN IN EXILE: a card matches a row by trait or by suit; a Wildcard matches only the Augment row; an Encounter matches no row. "Drawn from the Supplement deck" includes the card put on a new Bot deck at a reshuffle and a card resolved from the top of the Supplement deck. A Location played from the Bot deck stays in the Staging Area and is discarded at Clean-up.
- A reshuffle puts the top Supplement card on the new Bot deck although Khan's Captain says he does not enlist: the Bot ignores card text (REQ-SOLO-80).
- "Take an Incident to gain a Person" does both.
- "Gain an unmarked > Person / Cargo / Ship / Ally from the Junk": any unmarked card in the Junk comes first.
- Mind Control row: the Bot gains 2 Glory whenever you dismiss no Duty Officer, also when you cancel the attack (as the Georgiou Bot's Attack row does).
- Attack row: "you log this card" puts Revenge Is a Dish Best Served Cold into your Captain's Log and is part of the attack; if you cancel it, the card stays in the Staging Area. Any other card is logged by the Bot either way.
- ATTACK BOOST bonuses are attacks on the Bot, which cannot cancel them.

## Tests

- Given the Bot starts on the KHAN IN EXILE card, when it has 5 Dilithium at the end of its turn, it spends them, gains the top Encounter and switches to the regular cards.
- Given solo setup, then Ceti Alpha V and VI are out of the game and Genesis Device is the bottom card of the Supplement deck.
- Given the Bot in exile, when a Location is played from the Bot deck, then it is not placed in the Control Area.
- Given the Bot in exile, when a card leaves the Supplement deck, then the Bot gains 1 Dilithium.
- When the Bot gains a card with an unmarked trait, then it marks the first one in board order.
- Given 8 marked traits and a Duty Officer, when an Encounter resolves, then the Bot gains the best of the top 3 Encounters, destroys the other two and logs the gained card and the Encounter.
- At the end of the game the Bot scores 3 VP for each marked trait and 3 for each Focus icon.
