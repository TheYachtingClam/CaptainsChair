# Open questions from card specs

Collected from the "Rulings and open questions" sections of every card, board and command-card spec under `resources/scans/`. Each needs a decision before the code that depends on it is written.

## Rules questions

- **Cmdr. Burnham in Cadet Training** ([to_boldly_go/cards/captains/georgiou/2GEO13.md](to_boldly_go/cards/captains/georgiou/2GEO13.md)): Her attack forces the opponent to log a Duty Officer, or dismiss one so you gain 3 Glory. The virtual opponent has one Duty Officer (REQ-CTM-12) but the rules don't say which option it picks. Implemented as: it logs, so you gain nothing. Confirm.
- **Core Box Burnham variant** (REQ-CTM-21): The rule refers to a Burnham Status card, but no Crew deck with that card is in the content yet. Not implemented.
- **Ambassador Gral against an ignored attack** ([to_boldly_go/cards/person/2PER02.md](to_boldly_go/cards/person/2PER02.md)): His Reaction gives an Incident instead of returning it, and is an attack. If the opponent ignores it (Riva), the rules don't say what happens to the Incident. Implemented as: it is returned as normal. Confirm.
- **Attacks against the Cadet virtual opponent** (REQ-CTM-12): Implemented as: each attack works once against its "one of everything". Stealing takes 1 from the supply, removing Away Teams removes 1 (1 Glory for the Disruptor Pistols), and dismissing its Duty Officer still pays (2 Glory for Ash Tyler). Effects that only hurt it do nothing. Confirm.
- **Wildcard choice** (REQ-TR-07): The rules let the owner decide each time whether a Wildcard counts as the trait. Implemented as: your own Wildcard always counts for your own effects, without a prompt. This only matters when counting hurts you, for example the Universal Translator dismissing your Alien Ships. Confirm, or ask for a prompt in those cases.

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
