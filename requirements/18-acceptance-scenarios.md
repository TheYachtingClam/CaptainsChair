# 18 – Acceptance Scenarios (from Rulebook Examples)

Each rulebook example becomes an automated rules-engine test. Page numbers refer to the rulebook.

## AS-01 Resupply ordering and repeats (p. 9)

- **Given** *Xindi-Reptillian Battleship* is deployed, with RESUPPLY "Draw a card for every 2 Anomaly you have in play (max 4)".
- **And** 2 Anomaly traits are in play: *Forced Singularity*, and *Organians* beamed to *U.S.S. Shenzhou*.
- **And** *Vice Admiral Pasalk* is a Duty Officer, with "may discard a card to draw a card; repeat for each Ongoing".
- **And** 1 Ongoing is in play.
- **Then** the player draws 1 card and may discard-to-draw up to 2 times. They see each draw before choosing the next.

## AS-02 Taking control (p. 9)

- **Given** the player has the *Shenzhou* token and 2 Away Teams on *Archer IV*, and the opponent has 1 Away Team there.
- **When** the player takes control in the Control Step:
  - *Shenzhou* is dismissed to the Discard pile.
  - The player's 2 Away Teams return to their Captain.
  - The opponent's Away Team returns to their Captain.
  - The opponent gains 1 Glory.
  - *Archer IV* moves to the Location Area and its CONTROL resolves.
  - The Neutral Zone refills.
- **And** its RESUPPLY does not fire until the next turn.

## AS-03 Play without an action (p. 10)

- Playing *Set a Course*'s second PLAY (draw, discard, warp up to 2 Ships) spends no action.
- The card stays in the Staging Area.

## AS-04 Play with an action (p. 11)

- *Class C Shuttle* PLAY "Send an Away Team to a Location where you have a Ship" spends an action token, which is placed on the card.

## AS-05 Activation (p. 11)

- Activating *Denaxi Depot* exhausts it, spends 1 Latinum and discards a card.
- The player then finds a Ship anywhere except the Reserve deck, including the Discard pile.

## AS-06 Clean-up operation (p. 12)

- *Salt Vampires* CLEAN-UP forces logging a card from the Staging Area, and it may be itself.
- Cards that already left the Staging Area are not eligible.

## AS-07 Stardate resolution (p. 12)

- **Given** the opponent emptied Stardate #3 last turn and the player holds it.
- **When** the player's Clean-up reaches Stardate Resolution:
  - All 4 Market cards are junked; Glory on them returns to the supply.
  - Neutral Zone Locations without tokens are removed from the game.
  - *Argus Array*, which holds an opponent's Ship, stays.
  - Both areas refill before Glory Placement.

## AS-08 Glory placement and discarding (p. 13)

- The player places 1 Glory on *Universal Translator*; 5 remain on the Stardate.
- They discard selected hand cards and keep *Recruit*.
- Staging Area cards go to the Discard pile.
- The Duty Officer and the new Location stay.

## AS-09 Enlisting a Reserve mid-draw (p. 14)

- **Given** 2 cards are left in the deck and the player must draw 4.
- **Then** they draw 2, reshuffle the Discard pile, and put the top Reserve (*Cmdr. Saru*) on top.
- **And** they draw *Saru*, then 1 reshuffled card.

## AS-10 Enlisting a Development that costs an Incident (p. 14)

- **Given** the Draw and Reserve decks are empty.
- **When** the player enlists *Red Angel*, paying 3 Dilithium and taking an Incident:
  - The Incident counts toward hand size.
  - If the hand reaches 5, *Red Angel* stays on top of the deck undrawn.

## AS-11 Scan for a trait (p. 16)

- *Commander Shran*: "Scan for either Andorian or Weapon". The player chooses Weapon.
- There is no Weapon in the Person deck. The Andorians revealed there cannot be taken.
- The Ship deck yields *Holographic Drone Ship*. The other revealed cards are reshuffled into their decks.

## AS-12 Wildcard (p. 15)

- Bajoran + Klingon + Wildcard satisfies "3 Different Species".
- A Wildcard card may be discarded as an Engineer.
- An attack forcing the dismissal of a Cardassian cannot force a Wildcard card.

## AS-13 Deploy and warp (p. 18)

- *D'Kora Marauder* ATTACK PLAY deploys it and steals 1 Latinum.
- Later, exhaust it and spend 1 Dilithium to warp it to a controlled or neutral Location.

## AS-14 Away Team placement legality (p. 19)

- The player may send to *Argus Array* or *Dozaria*.
- The player may **not** send to *Tahal-Meeroj*, where the opponent's *Seleya* gives the opponent more Ships.
- After warping *Shenzhou* there to tie Ship counts, sending becomes legal.

## AS-15 Mission with beamed card (p. 20)

- Mission *Call in the Reinforcements*: Military at 6+, *Cmdr. Burnham* on duty, and an Incident beamed to *Shenzhou*.
- On completion, the Reward resolves: scan a Ship, free play it, gain 3 Dilithium.
- The conditional Klingon bonus fails, because the only Klingon, *Ash Tyler*, is beamed.
- The beamed Incident *Hostile Contact* is dismissed. *Burnham*, *Shenzhou* and *Tyler* stay.

## AS-16 Self-logging and Reactions (p. 21)

- *Bynars* PLAY gains a Cargo and logs itself.
- *V'Lar*'s Reaction ("after putting an Ally into play") still triggers.
- A later *Energy Drain* cannot count the *Bynars*' Engineer trait.

## AS-17 Entire Action Step (pp. 22–23)

A full turn with Soval. Verify each step in order:

1. *Seleya* activation promotes *Muroc*. *Vulcan*'s Passive allows a 2nd Duty Officer because one is Vulcan.
2. *Muroc* activation draws *Ti'Mur* from the Discard pile.
3. *Advisory*, which costs no action: spend 1 Dilithium, gain 1 Influence, draw. The deck reshuffles and enlists *Paan Mokar*, which is drawn.
4. *Advisory* also beams *United Earth* to the exhausted *Seleya*.
5. Action 1: *Paan Mokar* takes control. Its CONTROL free-plays *Ti'Mur*, since Research ≥ 5. The second PLAY deploys, warps and sends an Away Team.
6. *Ambassador Gral* finds *V'Lar* in the Reserve deck.
7. Action 2: *V'Lar* spends 1 Latinum to gain an Ally into hand.
8. *Vulcan* activation draws 2, because there are 3+ Away Teams on controlled Locations.
9. *Ti'Mur* activation discards *Stel* to beam *Kaelon II Science Ministry*. The *Vulcan Science Directorate* Reaction gives 1 Glory.
10. Action 3: *Infinite Diversity*. Remove an Away Team, dismiss *Ti'Mur* and its beamed card, log *Gral*, then take *Gomtuu* onto the deck. *Khitomer*'s Reaction on logging an Attack card gains an action.
11. Captain *Soval* activation dismisses *United Earth*, a Human, to draw 2 including *Gomtuu*.
12. Deploy *Gomtuu*. Action 4 gains 3 Military for 3 Research skills in play, excluding beamed cards.
13. Clean-up resets to 3 actions. Discard, then draw to 5.

## AS-18 Final scoring (p. 25)

See [13-final-scoring.md](13-final-scoring.md). The expected total is 24 VP.

## AS-19 Duplicate edge cases (p. 29)

- *Orb of Time* duplicating *Denobulans* logs the *Orb*.
- *Vadic's Splinter Group* duplicating *Cloaking Device* refreshes, draws and junks, but does not deploy.
- *Laas* duplicating *Orb of Time* only recalls.
