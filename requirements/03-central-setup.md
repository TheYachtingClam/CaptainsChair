# 03 – Central Setup

Source: Rulebook pp. 4–5.

The engine must perform central setup automatically, with player choices (Crew deck, first-player randomisation) collected in a pre-game lobby.

## 1. Setup procedure

- **REQ-CS-01 Market strip.** Create the Market between the players. It has slots, left to right: **Junk** space, **Person**, **Cargo**, **Ship**, **Ally**, and the **Incident** deck on the far side.
- **REQ-CS-02 Sort common cards.** Separate all common cards (no deck icon) into seven decks by suit: Person, Cargo, Ship, Ally, Encounter, Incident, Location.
- **REQ-CS-03 Market decks.** Shuffle the Person, Cargo, Ship and Ally decks. Place each facedown above its Market slot.
- **REQ-CS-04 Encounter deck.** Shuffle and place facedown near the Market.
- **REQ-CS-05 Incident deck.** Shuffle and place facedown on one side of the Market strip.
- **REQ-CS-06 Junk pile.** Reserve space on the other side of the Market strip for the Junk pile. The Junk pile starts empty.
- **REQ-CS-07 Reveal the Market.** Reveal one card from each of the four Market decks faceup into its Market slot.
- **REQ-CS-08 Location deck.** Split Locations by the position indicator at the bottom of each card into **Starting Locations** and **Advanced Locations**. Shuffle the Advanced Locations facedown.
- **REQ-CS-09** Shuffle the Starting Locations. Without revealing it, put one Starting Location on top of the Advanced Locations. This combined pile is the **Location deck**.
- **REQ-CS-10 Neutral Zone.** Draw 3 more Starting Locations and reveal them in a row. This row is the **Neutral Zone** (slots 1–3). Return the remaining Starting Locations to the box; they are out of the game.
- **REQ-CS-11 Stardate deck.** Select the Stardate cards for the chosen mode (for two players, cards marked "2-PLAYER"). Order them by sequence number, with #1 on top and the highest number at the bottom. Place the pile faceup. Other Stardate cards are out of the game.
- **REQ-CS-12 Supply.** Create an unlimited supply of Dilithium, Latinum and Glory.
- **REQ-CS-13 Stardate Glory.** Place on the top Stardate card the number of Glory tokens printed on it.
- **REQ-CS-14 Crew choice.** Each player chooses a Crew deck and takes all its cards and its Crew board. The first-game recommendation is Georgiou versus Soval, and the lobby should suggest it.
- **REQ-CS-15 Ship tokens.** Build a supply of Ship tokens for all common Ships and for both chosen Crew decks. Tokens of unused captains are excluded.
- **REQ-CS-16 Tokens per player.** Give each player 3 Action tokens and 3 Mission Completion tokens. Put the other Action tokens in the supply.
- **REQ-CS-17 First player.** Randomly determine the starting player and give them the Starting Player token.

## 2. Promo cards (optional)

- **REQ-CS-20** When creating a game, the host chooses whether to include promo cards. They are off by default.
- **REQ-CS-21** When promos are included, shuffle each promo card into the common deck of its suit during central setup, before the Market is revealed:
  - Cargo, Person, Ship and Ally promos go into their Market decks;
  - Incident promos go into the Incident deck;
  - Location promos go into the Starting or Advanced Location pile, according to their position indicator.
- **REQ-CS-22** A promo card's own SPECIAL setup text takes precedence. For example, *Subspace Rhapsody* replaces a random Incident in the Incident deck instead of adding to it.
- **REQ-CS-23** Promo cards follow all normal rules for common cards once in the game.

## 3. Combining boxes (optional)

Each Crew deck is balanced for its own box's Market cards. The app may later support mixing decks from this box ("To Boldly Go") with the Core Box.

- **REQ-CS-30** By default, only allow Crew decks from the same box as the common cards.
- **REQ-CS-31** When combining To Boldly Go with the Core Box:
  - **Duplicates.** Remove the 45 cards marked `•`, including the duplicate solo directive *Reinforce*.
  - **Replacements.** Remove the old versions of the 9 cards marked `†`.
  - **Stardate.** Use this box's Stardate cards.
  - **Market, Locations, Encounters.** Shuffle the remaining cards of each type together.
  - **Incidents.** Shuffle the remaining cards and return random cards to the box until 6 remain. Do this before adding Incidents from Crew decks.
  - **Junk.** After creating the Market, flip the top card of each of the four Market decks into the Junk pile.

## 4. Layout (for UI)

- **REQ-CS-40** The table view should show: Encounter deck, supply, Ship token supply, the four Market decks above the Market strip, the four faceup Market cards below it, Junk pile on one side, Incident deck on the other, Stardate pile with its Glory, Location deck, and the three-slot Neutral Zone between the two player areas.
