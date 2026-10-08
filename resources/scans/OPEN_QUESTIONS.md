# Open questions from card specs

Collected from the "Rulings and open questions" sections of every card, board and command-card spec under `resources/scans/`. Each needs a decision before the code that depends on it is written.

## Rules questions

- **Ambassador Gral against an ignored attack** ([to_boldly_go/cards/person/2PER02.md](to_boldly_go/cards/person/2PER02.md)): His Reaction gives an Incident instead of returning it, and is an attack. If the opponent ignores it (Riva), the rules don't say what happens to the Incident. Implemented as: it is returned as normal. Confirm.
- **Attacks against the Cadet virtual opponent** (REQ-CTM-12): Implemented as: each attack works once against its "one of everything". Stealing takes 1 from the supply, removing Away Teams removes 1 (1 Glory for the Disruptor Pistols), and dismissing its Duty Officer still pays (2 Glory for Ash Tyler). Effects that only hurt it do nothing. Confirm.
- **Wildcard choice** (REQ-TR-07): The rules let the owner decide each time whether a Wildcard counts as the trait. Implemented as: your own Wildcard always counts for your own effects, without a prompt. This only matters when counting hurts you, for example the Universal Translator dismissing your Alien Ships. Confirm, or ask for a prompt in those cases.

## Deferred until the Core Box is scanned

Not open for now. Leave these as they are and don't raise them again until the Core Box content is in `resources/scans/`.

- **Cmdr. Burnham in Cadet Training** ([to_boldly_go/cards/captains/georgiou/2GEO13.md](to_boldly_go/cards/captains/georgiou/2GEO13.md)): Her attack forces the opponent to log a Duty Officer, or dismiss one so you gain 3 Glory. The virtual opponent has one Duty Officer (REQ-CTM-12) but the rules don't say which option it picks. Implemented as: it logs, so you gain nothing. Confirm.
- **Core Box Burnham variant** (REQ-CTM-21): The rule refers to a Burnham Status card, but no Crew deck with that card is in the content yet. Not implemented.

## Rulings made while implementing the Crew decks

Each is implemented as described. Confirm, or say which to change.

- **Hemmer** (3PIK20): his Activation is offered only when you have a secured neutral Location to take, so he is never logged for nothing.
- **Lt. Spock** (3PIK21): his RESUPPLY asks before exhausting him. The printed text has no "may", but the exhaust is the price of the effect.
- **Starbase One** (3PIK03): the draw Activation is offered even with fewer than 2 Ships, as the spec has no requirement; it then draws nothing.
- **William T. Riker** (3RIK01): his first Activation is offered only when a card in hand shares a suit with one in your Discard pile.
- **Chateau Picard** (3RIK10): the second PLAY is offered only when there is an Incident to return. In Cadet Training its CLEAN-UP gives Glory only to you.
- **Deanna Troi-Riker** (3RIK15): "Refresh your Captain" is offered only when the Captain is exhausted.
- **U.S.S. Zheng He and Proximity Blast** (3RIK06, 3RIK07) in Cadet Training: the virtual opponent has no Ships at Locations (REQ-CTM-12), so their attacks do nothing.
- **T88 Diagnostic Tool** (3FRE07): replaces only gains of a single suit; for "a Person or Ship" the "same suit" is unclear, so it is not offered.
- **Kayshon and Shax** (3FRE09, 3FRE10) in Cadet Training: the virtual opponent counts as having 1 Spy, and an Away Team at every neutral Location.
- **Rebelution** (2REB15): dismisses only your own Helmets, and not ones in your Staging Area, which cannot be dismissed (KW-DSM-04).
- **Rebner's deck in Cadet Training**: the Clumpships draw 1 card for the virtual opponent's Ship but the forced log does nothing; Rumdar may dismiss its Spy for 1 Glory; Big Enough Helmet's cost has nobody to draw.
- **Put into play after playing** (KW-PIP-01, AS-16): a played card now counts as put into play after its PLAY resolves even when the PLAY moved it away again (logged, returned, recalled). Before, cards that left play did not count. This is what the rulebook example (Bynars and V'Lar) needs.

## Rulings made while implementing Khan

Answered by you on 2026-10-07, and implemented:

- **The Captain flips** only by the reward of the mission *I Shall Leave You as You Left Me*. Ceti Alpha VI flips only Ceti Alpha V.
- **Khan Noonien Singh's second PASSIVE** is mandatory and can trigger any number of times; the Wrathful side's is an optional REACTION.
- **A Wildcard card** can mark either opponent-dependent entry. **Khan against Khan** uses Augment and Human. **"The same card"** means the physical card.
- **The trait tokens' board order** is alphabetical, then the two opponent-dependent entries.
- **Devastated Ceti Alpha V** (2KHA02B): "Send all of your Away Team here" moves every one of Khan's Away Teams there, from his Captain and from every other Location.
- **Marla McGivers** (2KHA13): her CLEAN-UP logs her whenever Devastated Ceti Alpha V is exhausted, even when Ceti Eel is not in the Development pile.
- **Wrathful Khan** (2KHA01B): "ignore all requirements" treats every Specialty track as being at its top, so a check such as "if [Military] is at 5+" on any card succeeds.

Made while writing the code. Each is implemented as described. Confirm, or say which to change.

- **The two opponent entries** (cb-khan): at most one of them may use a trait that is also printed on the board. This is what the rulebook's Soval example needs: Vulcan plus Ambassador or Telepath, never Ambassador and Telepath together.
- **Devastated Ceti Alpha V** (2KHA02B): its ACTIVATION can be used with an Away Team there: it draws nothing but exhausts the card, which Marla McGivers looks for.
- **Marla McGivers** (2KHA13): she counts herself as a Starfleet card in play for her PLAY.
- **Ceti Eel** (2KHA08): offered only while the opponent has a Duty Officer. If the attack is ignored, no Duty Officer is dismissed and no Away Teams are sent; the card still returns to the Development pile and the opponent may still draw.
- **Cpt. Terrell** (2KHA06): "at no Dilithium/Latinum/Incident cost" keeps conditions such as "have Marla McGivers logged". Terrell in the Staging Area is himself a Mind Control Person in play.
- **Revenge Is a Dish Best Served Cold** (2KHA10): "mark one trait of it" reads the card's own traits; a Wildcard does not count there. If the second PLAY's attack is ignored, nothing is given.
- **Khan's three Incidents** (2KHA19 to 2KHA21): the Glory and the opponent's draw depend only on the revealed card, not on whether the attack was ignored. In Cadet Training the card is returned and you gain 1 Glory, as when an Incident is given to the virtual opponent.
- **Genesis Device** (2KHA11): "mark any one trait" may fill an opponent entry with any trait allowed for it. A destroyed neutral Location is replaced from the Location deck.
- **S.S. Botany Bay** (2KHA16): an effect that offers Ships to warp may still list it; choosing it does nothing.
- **Marooned for All Eternity** (cb-khan): the opponent chooses one of their Duty Officers or beamed Persons; a Person in their Staging Area cannot be chosen.
- **Wrathful Khan** (2KHA01B): a Best Focus icon counts as one Focus icon for his ENDGAME.

## Rulings made for the Five-Year Mission bonuses and challenges

- **Boosts with a cost** ("take an Incident to …", "spend 1 [Dilithium] to …") are optional: the human is asked each game, and the Boost is skipped when the cost cannot be paid. Boosts without a cost always resolve.
- **Boosts with no moment printed** ("BOOST: Gain an [Action].") resolve at the start of the game: after the starting hand and the "after drawing" Boosts, before the first turn. An Action gained then lasts through the first turn.
- **Before drawing the starting hand:** cards found or taken then stay in hand, and the full starting hand is drawn afterwards.
- **The same Boost twice:** losing to the same Bot again may offer a Boost you already have. Taking it again adds a second copy, which resolves twice.
- **Pike's LOSS REINFORCE** ("a card with [Research]/[Influence]/[Military]") counts [Any Skill] cards.
- **Option B with nothing to choose:** a REINFORCE bonus with no qualifying card cannot be taken. With no option A card and no option B available (for example Rules of Acquisition after a success), there is no upgrade.
- **Live Long and Prosper:** after exactly one success, the human chooses on the assignment form which resource to start without.
- **Two Weeks to the Closest Outpost, They Will Arrive on Tuesday:** "after a success" means the previous assignment was a success. After a failure, Tuesday sets one Away Team aside again.
- **Only Ship in the Quadrant:** the assignment fails only when the starting Ship is dismissed or recalled, as printed; logging or destroying it does not.

## Gaps in the CLAUDE.md action list

None. Every action named in the specs is in the CLAUDE.md action list.
