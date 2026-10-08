# 11 – Captain's Log and Hidden Information

Source: Rulebook p. 21.

## 1. Captain's Log

- **REQ-LOG-01** **Logging** a card places it under the player's Captain card permanently. This thins the deck.
- **REQ-LOG-02** With very few exceptions, logged cards cannot be used again. They still **count for final scoring**.
- **REQ-LOG-03 Self-logging cards.** Cards whose PLAY operation ends with "Log this card" go to the Staging Area, resolve, then move to the Log.
  - The card, with its suit and traits, is in play only during its own operation.
  - It cannot count toward missions or trait-counting effects evaluated before or after.
  - It **does** count as having been "put into play", so it triggers "after putting X into play" Reactions.
- **REQ-LOG-04** The engine must model a card's zone transitions precisely so that trait counts reflect the moment of evaluation.

## 2. Secret versus public information

- **REQ-INF-01 Secret:**
  - Each player's hand is hidden from the opponent.
  - The order of every facedown deck is hidden from everyone, including the owner.
  - Facedown common decks are unknown to both players.
- **REQ-INF-02 Public:**
  - Junk pile, Discard piles, Development piles and beamed cards.
  - Captain's Logs. See §3.
  - The full composition of the common decks. Provide the common card list in-app.
- **REQ-INF-03** The server is the authority on hidden state. Clients must receive only the information their player may see. The opponent's hand is sent as a count only, and deck order is never sent.
- **REQ-INF-04** Players can browse public zones at any time.
- **REQ-INF-05** A player may look through what is in their own Reserve deck at any time, to get to know their Crew. Only the contents are shown, sorted by name and labelled as not being the deck's order; the order stays hidden from everyone (REQ-INF-01). The opponent does not see it, because cards can be put onto a Reserve deck from hand.

## 3. Viewing the Captain's Log (online ruling)

The printed rules disagree. Page 21 lists Logs as public, and page 31 says only the owner may look. The developers' errata settles it: the owner may go through their Log, and the opponent may **ask** about its contents, which the owner must answer truthfully. The errata's aim is to avoid slowing the tabletop game. In the online game a click is faster than a question, so the Log is simply viewable.

- **REQ-LOG-10** Clicking a player's Captain's Log opens a viewer showing every logged card, faceup, with full card details.
- **REQ-LOG-11** Both players can open **either** player's Log at any time, on either player's turn. This matches the errata, since the opponent could learn everything by asking.
- **REQ-LOG-12** Opening the Log viewer is read-only. It never counts as interacting with the Log for rules purposes; cards there stay out of play.
- **REQ-LOG-13** The Log pile on the table shows its card count. The viewer should also show useful totals, such as printed VP and Incident count, since these matter for final scoring and the Burn.
- **REQ-LOG-14** The server sends Log contents to both clients as public state.
