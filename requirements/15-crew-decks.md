# 15 – Crew Decks and Deck-Specific Rules

Source: Rulebook pp. 34–35.

Each Crew deck is a content pack of cards, a Crew board and Ship tokens. Some decks change core rules. The engine must let a deck override hand size, Reserve behaviour, Specialty tracks and scoring through configuration or hooks, not special-case code scattered through the engine.

## 1. Deck summaries (for the deck-selection screen)

| Captain | Faction | Complexity | Theme and play style |
|---|---|---|---|
| Georgiou | Starfleet | 2/10 | Explorer of alien life. Collects trusted colleagues such as *Saru*, *Sarek* and *Burnham*. Must also build Military for the Klingon war. Has Starfleet tech such as the *Red Angel* suit. |
| Soval | Vulcan | 3/10 | Values Scientists and dismisses Time Travel and Human contacts. Choice between the Military route (*Vulcan Hello*), T'Pau's Influence route, and Research toward the *Path of Surak*. |
| Kirk | Starfleet | 4/10 | Versatile. Pursues Research, Influence and Military together. Has the most Any Skill icons. Visits *Strange New Worlds* and gets the most Encounters. |
| Archer | Starfleet | 6/10 | First Starfleet captain with limited resources and few Away Teams. Builds crew from the Person deck. Research via *T'Pol*. Xindi: war or alliance. |
| Rebner | Pakled | 8/10 | Helmets, hand size 3, junking and digging in the Junk. Clumpships. |
| Khan | Augment | 9/10 | No Specialty tracks. Marks collected traits instead. Incident management and double-sided cards. |

- **REQ-CD-01** Show complexity and summary text on the selection screen. Recommend Georgiou versus Soval for first games.

## 2. Archer

- **REQ-CD-ARC-01 Away Teams "2+".** Archer starts with 2 Away Teams on the Captain. The other 4 are kept nearby and out of play; some of Archer's Developments refer to them. The engine needs an "out-of-play Away Team reserve" zone.
- **REQ-CD-ARC-02 Archer's Reserve.** Some cards put a card on top of the Reserve deck, even if the Reserve deck was empty. This recreates it, so a later reshuffle enlists from the Reserve again, even after a Development was enlisted earlier.

## 3. Rebner (Pakled)

- **REQ-CD-REB-01 Hand size 3.** Draw 3 in player setup and refill to 3 each Clean-up.
- **REQ-CD-REB-02** Research and Influence multipliers are always **0**, even on the Basic side. Advancing those tracks only helps meet requirements. This also applies to a Rebner Bot in solo play.
- **REQ-CD-REB-03 Helmets.** Many cards use the Helmet trait and the *wearing* keyword ([14-keywords.md](14-keywords.md)). Every Pakled Person gets stronger when wearing a helmet.
- **REQ-CD-REB-04** The Directives *Pakled Decree* and *Samaritan Snare* are Ongoing. They can only be used while the player has the helmet for them.
- **REQ-CD-REB-05** A Helmet beamed to a Location or a Directive can return to the deck only through the card *Rebelution*.
- **REQ-CD-REB-06** The deck makes heavy use of junking and gaining from the Junk.

## 4. Khan (Augment)

- **REQ-CD-KHN-01 Double-sided cards.**
  - The Captain card starts showing its normal side. The *Wrathful* side must be hidden at game start.
  - *Ceti Alpha V* starts non-devastated. The *Devastated* side is hidden.
  - When the Captain flips, move any Away Teams on it to the other side.
- **REQ-CD-KHN-02 Hand size.** *Ceti Alpha V* raises hand size. Draw 6 in player setup and refill to 6 each Clean-up until it flips to *Devastated Ceti Alpha V*.
- **REQ-CD-KHN-03 No Reserve deck.** "Enlist a Reserve" does nothing for Khan. Per his Captain card, he does not enlist when the deck cycles. His main way to enlist Developments is on *Devastated Ceti Alpha V*, built around Augment cards.
- **REQ-CD-KHN-04 No Specialty tracks.** Effects that gain Research, Influence or Military do nothing for Khan.
  - Before the Captain flips, Khan cannot meet Specialty restrictions.
  - After it flips to *Wrathful*, he automatically meets them all.
- **REQ-CD-KHN-05 Focus icons.** Before *Wrathful* they score 0. After *Wrathful* they score 1 or 3 VP each, depending on how many traits are marked. Thresholds are on the board data.
- **REQ-CD-KHN-06 Trait marking.** The board has 12 Trait Mark tokens, starting unmarked.
  - After **gaining** a card or **taking control** of a Location with an unmarked trait from the board, Khan may mark one such trait.
  - A Wildcard counts as any single trait for this. No Market or common Location card currently has Wildcard.
- **REQ-CD-KHN-07** **Taking** a card, such as an Encounter or Incident, or being given one, does **not** allow marking.
- **REQ-CD-KHN-08** Each trait can be marked once, in any order. The choice is made immediately on gaining, or before resolving CONTROL, and cannot be changed.
- **REQ-CD-KHN-09 Opponent-dependent entries.** Two entries depend on the opponent's Captain.
  - They must be marked with two **different** traits from the opponent's Captain, excluding Human if possible.
  - Either may repeat a trait already on the board, but the same card cannot mark both.
  - Examples:
    - Against Archer: any two of NX-01, Pilot and Starfleet.
    - Against Kirk: Starfleet and Human, because Kirk has no other traits.
    - Against Soval: one Captain-specific entry is Ambassador or Telepath, and the other is Vulcan.
- **REQ-CD-KHN-10 Khan in Cadet mode.**
  - Pick a random other Captain to set the two opponent-dependent traits.
  - *Revenge Is A Dish Best Served Cold*'s first operation may mark a trait from a card in the Junk.
  - When its second operation would log it and an Incident into the opponent's Log, destroy both cards and gain 4 Glory instead.
- **REQ-CD-KHN-11 Khan as Bot (solo).**
  - Remove *Ceti Alpha V* and *Ceti Alpha VI*. The Bot never flips its Captain.
  - The Bot marks one trait when a card is gained, taken under control or **taken**. With several unmarked traits it marks the first applicable one on the board, top to bottom and left to right.
  - Told to "mark a trait", it uses the same tie-breaker.
  - "Unmarked" on Automated Command cards means "any unmarked trait". Among cards with unmarked traits it prefers the highest-value card.
  - Supplement deck: shuffle all Developments except *Genesis Device*, then put *Genesis Device* on the bottom. Solo Challenge cards for the Bot's Reserve go on top of the Supplement deck.
  - Set aside the two regular Automated Command cards. Use the "KHAN IN EXILE" card, which says when to swap to the regular cards on the "TRAITS" and "SUITS WITH NO DUTY OFFICER" side.
  - Follow the special rules at the top of the currently active command card.

## 5. Card content

- **REQ-CD-90** Every card in every deck must be transcribed as data. The rulebook only shows examples; the complete card list must come from the physical cards or the publisher's card list.
- **REQ-CD-91** Card names mentioned in the rulebook, useful as test fixtures:
  - Utilize, Recruit, Set a Course, Class C Shuttle, U.S.S. Shenzhou, Salt Vampires, Strange New Worlds, Red Angel.
  - Kamran Gant, Advisory, Infinite Diversity in Infinite Combinations, Vulcan Science Directorate, Paan Mokar, Ti'Mur, Seleya, Muroc, V'Lar, Ambassador Gral, Gomtuu, Khitomer, Vulcan.
  - Orb of Time, Vadic's Splinter Group, Laas, Denobulans, Cloaking Device, Rebelution, Ceti Alpha V, Genesis Device, Revenge Is A Dish Best Served Cold.
