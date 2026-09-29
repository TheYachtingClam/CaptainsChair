# 17 – Quick Reference, Common Terms and Icon Catalogue

Source: Rulebook p. 36 and the player aids.

This is the in-app quick-reference panel, and the enumerations the data model must support.

## 1. Overview of play

- A turn has four steps: **Resupply, Control, Action, Clean-up**.
- **The game ends when either:**
  - The last Stardate card empties and triggers a Resolution. Play continues until both players have had equal turns, then each plays one more turn, then final scoring.
  - The Incident deck empties and triggers the Burn. The player with fewer Incidents wins, counting hand, play, Discard pile, Draw deck and Log but not the Reserve deck. On a tie, go to final scoring.
- **Final scoring:**
  - Glory tokens, not counting Glory on cards.
  - Tokens on neutral Locations.
  - ENDGAME operations on cards in play.
  - Printed VP.
  - Focus icons times multipliers, only if a mission was completed.
  - Completed missions, Advanced side only.
- **Substituting resources:** 1 Glory = 2 Dilithium, or 1 Latinum.

## 2. Common terms

| Term | Meaning |
|---|---|
| Gain, Scan | New card from the Market to the top of the Draw deck or the Discard pile |
| Take | Directly to hand, e.g. from the Incident or Encounter deck |
| Enlist | New card from the Reserve deck or Development pile to the top of the deck |
| Find | Matching card from hand, Draw deck, Discard pile or Reserve deck into hand |
| Deploy | From the Staging Area to the Fleet Area |
| Recall | From play to hand |
| Dismiss | From play to the Discard pile |
| Discard | From hand, or the top of a named deck, to the Discard pile |
| Promote | Move a Person to the Duty Officer slot. Limit: 1 |
| Log | Move to the Captain's Log |
| Junk | Move to the Junk pile |
| Destroy | Return to the box |

## 3. Enumerations

### Card suits

Ally†, Captain, Cargo†, Directive, Encounter, Incident, Mission\*, Location, Person†, Ship†

- † marks the Market suits.
- \* marks items not used in this box. They must still exist in the data model for future content.

### Species traits

Any Species, Different Species, Alien, Aenar, Andorian, Android, Bajoran, Betazoid\*, Borg, Breen, Cardassian, Changeling, Ferengi, Human, Hirogen\*, Jem'Hadar\*, Kazon, Kelpien, Klingon, Orion, Pakled, Reman\*, Romulan, Synthetic, Talaxian\*, Tellarite, Transcendent, Trill\*, Vau N'Akat, Vorta\*, Vulcan, XB\*, Xindi

### Regular traits

Ambassador, Ancient, Anomaly, Augment, Beverage, Business, Cloak, Communication, Creature, Crossover\*, Doctor, Dominion, Engineer, Helmet, Hologram, Imperial, Mind Control, Ops, Path of Surak, Pilot, Maquis\*, NX-01, Scientist, Security, Shady, Spy, Starbase, Starfleet, Telepath, Time Travel, Weapon

### Other (special) traits

Attack, Lower Decker\*, Ongoing, Surprise, Wildcard

### Other icons

- **Specialty icons:** Research, Influence and Military. Each comes as a Skill, a Focus and a Restriction.
- **Combined icons:** Any Skill, Best Focus, Variable Skill ("?").
- **Tokens and scoring:** Victory Points, Action token, Away Team, Dilithium, Latinum, Glory.
- **Not used in this box:** Borg Collective\*, Borg Drone\*, Treachery\*.

- **REQ-REF-01** Every icon needs an accessible text label and a tooltip. Text must never rely on colour alone.
- **REQ-REF-02** Hovering or tapping a keyword in card text opens its entry in [14-keywords.md](14-keywords.md).
