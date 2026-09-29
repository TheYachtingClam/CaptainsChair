# 13 – Final Scoring

Source: Rulebook pp. 24–25.

## 1. When scoring happens

- **REQ-FS-01** Final scoring happens if the game ended by a **Resolution** or by a **tie in the Burn**.
- **REQ-FS-02** Before scoring, remove all cards left in each player's **Reserve deck** and **Development pile**. They do not count.
- **REQ-FS-03** Every other card the player owns counts, wherever it is. This includes the Captain's Log and beamed cards.

## 2. Score components

A player's score is the sum of:

1. **Glory**: 1 VP per Glory token in the resource pool. Glory on the player's cards in play does not count.
2. **Neutral presence**: 1 VP per Away Team or Ship token the player has on **neutral** Locations.
3. **ENDGAME operations** on the player's **in-play** cards, usually the Captain and controlled Locations.
   - Endgame conditions about unique traits count any number of Wildcard traits as a single unique trait.
4. **Printed VP**: the sum of printed VP on all the player's cards. Some values are negative.
   - **Asterisk VP**: if the VP icon has an asterisk, the card's SPECIAL operation explains how it scores, even if it is not in play.
5. **Focus icons**: for each Specialty track, multiply the highest multiplier reached by the number of cards with that Focus icon.
   - A Best Focus card scores the highest multiplier reached on **any** track.
   - If the player completed **no missions**, skip this component entirely.
6. **Advanced missions**: on the Advanced side, add the printed VP of each mission with a Mission Completion token.

## 3. Clarifications

- **REQ-FS-10 Unused Endgame.** A card with an ENDGAME operation that is not in play, because it is logged or still in the deck, scores its printed VP. Its ENDGAME operation is not evaluated.
- **REQ-FS-11 Wildcard.** Wildcard traits do **not** count as any other trait during final scoring.
- **REQ-FS-12 Resources on cards** during scoring are not the player's. Glory there does not score and does not count toward ENDGAME conditions.
- **REQ-FS-13** After ENDGAME operations are scored, card location no longer matters.

## 4. Winner

- **REQ-FS-20** The player with the higher total VP wins. **On a tie, both players win.**

## 5. Score screen

- **REQ-FS-30** Show a per-player breakdown matching the score pad: Glory, tokens on neutral Locations, Endgame, printed VP, each Focus track with multiplier and count, Advanced missions, and total.

## 6. Worked example (acceptance test)

The rulebook example scores 24 VP for Soval:

| Source | VP |
|---|---|
| Printed VP: *T'Pau* 4, *Phlox* 1, *Vice Admiral Pasalk* 1 | 6 |
| Soval's ENDGAME: 1 per Person, excluding Vulcans. Only *Phlox* and *Riva* qualify | 2 |
| Influence Focus: *Riva*, *Minister Kuvak*, *Holographic Drone Ship*, *Khitomer* at ×4 | 16 |
| **Total** | **24** |

Setup notes for the test:

- Influence has passed the ×4 multiplier.
- At least one mission is complete.
- The example ignores Person cards from the Available and Reserve decks because they are Vulcan. The two enlisted Developments are Vulcan too, so they add nothing to Soval's ENDGAME.
