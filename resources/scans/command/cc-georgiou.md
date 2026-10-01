---
id: cc-georgiou
name: Georgiou Automated Command cards
suit: Automated Command
deck: georgiou
scan: cc-georgiou.pdf
sides:
  - cc-georgiou-suits-no-duty-officer   # PDF page 1
  - cc-georgiou-suits-duty-officer      # PDF page 2
  - cc-georgiou-traits                   # PDF page 3
  - cc-georgiou-upgrades                 # PDF page 4
---

# Georgiou Automated Command cards

The Bot playing Georgiou's Crew deck resolves every card with these rows instead of the card's own text (REQ-SOLO-80 to REQ-SOLO-83). Each row becomes one function in `server/engine/bot/georgiou.py`, following the Bot action rules in CLAUDE.md.

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

Image id: `cc-georgiou-traits`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Surprise | Resolve this card's Surprise operation. | 1. Resolve the card's SURPRISE (Bot only) operation instead of any row. |  | yes |
| 2 | Anomaly | Junk the most valuable card in the Market (ignoring any with tokens). Gain an Incident. Log this card. Resolve the top card of the Bot deck. | 1. Junk the Market card most valuable to the human, ignoring cards with tokens (REQ-SOLO-150).<br>2. Gain an Incident to the Bot Discard pile.<br>3. Log this card.<br>4. Resolve the top card of the Bot deck. | `JUNK`, `TAKE_INCIDENT`, `LOG`, `RESOLVE_CARD` | no |
| 3 | Kelpien | Log the top card of the Bot deck. Gain 1 [Research]. Continue resolution. | 1. Log the top card of the Bot deck.<br>2. Gain 1 Research.<br>3. Continue resolution. | `LOG`, `GAIN_SPECIALTY`, `CONTINUE_RESOLUTION` | yes |
| 4 | Vulcan | Discard the top card of the Bot deck. Gain 1 [Influence]. Continue resolution. | 1. Discard the top card of the Bot deck.<br>2. Gain 1 Influence.<br>3. Continue resolution. | `DISCARD`, `GAIN_SPECIALTY`, `CONTINUE_RESOLUTION` | yes |
| 5 | Security / Ops | **You remove [Away Team].** Gain Spy / Klingon if able. Otherwise, gain 1 [Military] and 1 [Glory]. If this card is a Person, promote it to Duty Officer. | 1. The human removes one of their Away Teams (attack part).<br>2. Gain the most valuable Spy or Klingon if able; otherwise gain 1 Military and 1 Glory.<br>3. If this card is a Person, promote it. | `ATTACK`, `REMOVE_AWAY_TEAM`, `GAIN_CARD`, `GAIN_SPECIALTY`, `GAIN_RESOURCE`, `PROMOTE` | no |
| 6 | Attack | If [Research] is higher than [Military], gain 1 [Glory] and continue resolution. Otherwise: Dismiss Duty Officer if able, otherwise take an Incident. **You dismiss a Duty Officer, if able**, otherwise the bot takes Kelpien / Vulcan > Ship and gains 1 [Research]. If this card is a Person, promote it to Duty Officer. | 1. If the Bot's Research is higher than its Military: gain 1 Glory and continue resolution.<br>2. Otherwise: dismiss the Bot's Duty Officer if it has one, else the Bot takes an Incident.<br>3. Then the human dismisses one of their Duty Officers if they have one (attack part); if they cannot, the Bot takes the most valuable Kelpien or Vulcan, else a Ship, and gains 1 Research.<br>4. If this card is a Person, promote it. | `GAIN_RESOURCE`, `CONTINUE_RESOLUTION`, `DISMISS`, `TAKE_INCIDENT`, `ATTACK`, `GAIN_CARD`, `GAIN_SPECIALTY`, `PROMOTE` | no |

## SUITS WITH NO DUTY OFFICER

Image id: `cc-georgiou-suits-no-duty-officer`.

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Log the top card of the Bot deck. Gain a Person. Return this card. | 1. Log the top card of the Bot deck.<br>2. Gain the most valuable Person.<br>3. Return this card. | `LOG`, `GAIN_CARD`, `RETURN_INCIDENT` | no |
| 2 | Ship | Deploy this Ship; it explores. If a Person is in Bot Discard pile, send an [Away Team] to a neutral Location. | 1. Deploy and explore.<br>2. If the Bot Discard pile has a Person, send an Away Team to a neutral Location. | `DEPLOY`, `EXPLORE`, `SEND_AWAY_TEAM` | no |
| 3 | Ally | Discard the top 2 cards of the Bot deck. If a Person is in Bot Discard pile, gain 1 [Research] / [Influence] / [Military] (whichever is lower). For each Ship in Bot Discard pile, send an [Away Team] to a neutral Location. Log this card. | 1. Discard the top 2 cards of the Bot deck.<br>2. If the Bot Discard pile has a Person, gain 1 in the lowest Specialty.<br>3. Send one Away Team to a neutral Location per Ship in the Bot Discard pile.<br>4. Log this card. | `DISCARD`, `GAIN_SPECIALTY`, `SEND_AWAY_TEAM`, `LOG` | yes |
| 4 | Cargo | Discard the top 2 cards of the Bot deck. Send an [Away Team] to a neutral Location. Take a Person. Log this card. | 1. Discard the top 2 cards of the Bot deck.<br>2. Send an Away Team to a neutral Location.<br>3. Take the most valuable Person onto the Bot deck.<br>4. Log this card. | `DISCARD`, `SEND_AWAY_TEAM`, `GAIN_CARD`, `LOG` | no |
| 5 | Person | Log the top card of the Bot deck. Gain 1 [Research] / [Military] (whichever is lower). Send an [Away Team] to a neutral Location. Promote this card to Duty Officer. | 1. Log the top card of the Bot deck.<br>2. Gain 1 in the lower of Research and Military.<br>3. Send an Away Team to a neutral Location.<br>4. Promote this card. | `LOG`, `GAIN_SPECIALTY`, `SEND_AWAY_TEAM`, `PROMOTE` | yes |
| 6 | Directive | Gain a Ship / Ally and take an Incident. Send an [Away Team] to a neutral Location. | 1. Gain the most valuable Ship or Ally.<br>2. Take an Incident onto the Bot deck.<br>3. Send an Away Team to a neutral Location. | `GAIN_CARD`, `TAKE_INCIDENT`, `SEND_AWAY_TEAM` | no |
| 7 | Encounter | Log the top 2 cards of the Bot deck. Take a Ship. Log this card. | 1. Log the top 2 cards of the Bot deck.<br>2. Take the most valuable Ship onto the Bot deck.<br>3. Log this card. | `LOG`, `GAIN_CARD` | no |
| 8 | Location | Discard the top card of the Bot deck. Return an Incident from Bot Discard pile if able, otherwise gain 1 [Glory]. | 1. Discard the top card of the Bot deck.<br>2. Return the topmost Incident from the Bot Discard pile; if there is none, gain 1 Glory. | `DISCARD`, `RETURN_INCIDENT`, `GAIN_RESOURCE` | yes |

## SUITS WITH DUTY OFFICER

Image id: `cc-georgiou-suits-duty-officer`.

Used while the Bot has a Duty Officer. Flip back when it is dismissed or logged (REQ-SOLO-91 to REQ-SOLO-95).

| # | Matches | Printed | Steps | Actions | Undoable |
|---|---|---|---|---|---|
| 1 | Incident | Send an [Away Team] to a neutral Location. Gain 1 [Military]. Return this card. | 1. Send an Away Team to a neutral Location.<br>2. Gain 1 Military.<br>3. Return this card. | `SEND_AWAY_TEAM`, `GAIN_SPECIALTY`, `RETURN_INCIDENT` | yes |
| 2 | Ship | Gain 1 [Research]. Deploy this Ship; it explores. Send an [Away Team] to a neutral Location. | 1. Gain 1 Research.<br>2. Deploy and explore.<br>3. Send an Away Team to a neutral Location. | `GAIN_SPECIALTY`, `DEPLOY`, `EXPLORE`, `SEND_AWAY_TEAM` | no |
| 3 | Ally | Discard the top card of the Bot deck. Gain a Kelpien > Ally. Log Duty Officer. Log this card. | 1. Discard the top card of the Bot deck.<br>2. Gain the most valuable Kelpien; else an Ally.<br>3. Log the Duty Officer and flip SUITS.<br>4. Log this card. | `DISCARD`, `GAIN_CARD`, `LOG` | no |
| 4 | Cargo | Log the top card of the Bot deck. Discard the top 2 cards of the Bot deck. Gain a Ship. Deploy the gained Ship; it explores. Log Duty Officer. | 1. Log the top card of the Bot deck.<br>2. Discard the next 2.<br>3. Gain the most valuable Ship, deploy it and explore.<br>4. Log the Duty Officer and flip SUITS. | `LOG`, `DISCARD`, `GAIN_CARD`, `DEPLOY`, `EXPLORE` | no |
| 5 | Person | Log the top card of the Bot deck. Send an [Away Team] to a neutral Location. | 1. Log the top card of the Bot deck.<br>2. Send an Away Team to a neutral Location. | `LOG`, `SEND_AWAY_TEAM` | yes |
| 6 | Directive | If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter then log this card. Otherwise, gain a [Research Focus]/[Military Focus] > Anomaly > Cargo. | 1. If the Bot can both log one of its controlled Locations and remove 2 of its Away Teams: do both, take the top Encounter onto the Bot deck, then log this card.<br>2. Otherwise gain the most valuable card with a Research or Military Focus; else an Anomaly; else a Cargo. | `LOG`, `REMOVE_AWAY_TEAM`, `TAKE_ENCOUNTER`, `GAIN_CARD` | no |
| 7 | Encounter | Gain 1 [Research] / [Military] (whichever is higher). Take a Vulcan > Ally > Ship. Log this card. | 1. Gain 1 in the higher of Research and Military.<br>2. Take the most valuable Vulcan; else an Ally; else a Ship.<br>3. Log this card. | `GAIN_SPECIALTY`, `GAIN_CARD`, `LOG` | no |
| 8 | Location | Log the top 2 cards of the Bot deck. Gain 1 [Research]. Log Duty Officer. | 1. Log the top 2 cards of the Bot deck.<br>2. Gain 1 Research.<br>3. Log the Duty Officer and flip SUITS. | `LOG`, `GAIN_SPECIALTY` | yes |

## Five-Year Mission upgrades

Image id: `cc-georgiou-upgrades`. Used only in the solo campaign (REQ-CAMP-25 to REQ-CAMP-31).

### WIN

- **A. Common card types you can reinforce:** Security / Ops / Kelpien
- **B. Alternative bonuses, pick 1:**
  - REINFORCE: A Person from your Available cards and/or a Person from your Reserve deck.
  - BOOST: After drawing the starting hand, draw a card and gain an [Action].

### LOSS

- **A. Common card types you can reinforce:** Starfleet
- **B. Alternative bonuses, pick 1:**
  - REINFORCE: A Person from your Available cards or Reserve deck.
  - BOOST: Gain an [Action].

## Rulings and open questions

- Georgiou has no Bot special rule.
- In the Attack row, "Dismiss Duty Officer" is the Bot's own Duty Officer and is not an attack; only the bold part targets the human.
- The Security / Ops row's "You remove [Away Team]" has no Location stated; the human picks which of their Away Teams to remove.
- Solo rulebook p. 7: resolving Vulcan Science Academy uses the Vulcan row, then continues to the Location row on the SUITS card.

## Tests

- Given a Vulcan Location is resolved, then the Bot discards the top card, gains 1 Influence, and continues to its SUITS Location row.
- Given the Bot's Research is 5 and Military 3, when an Attack card is resolved, then the Bot gains 1 Glory and continues resolution.
- Given the Bot has no Duty Officer and the human has none either, when the Attack row resolves the Otherwise branch, then the Bot takes an Incident and takes a Kelpien or Vulcan.
