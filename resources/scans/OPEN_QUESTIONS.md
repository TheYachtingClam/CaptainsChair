# Open questions from card specs

Collected from the "Rulings and open questions" sections of every card, board and command-card spec under `resources/scans/`. Each needs a decision before the code that depends on it is written. Answered and confirmed items are removed from this file; their rulings live in the card specs and in `requirements/`.

## Rules questions

None open.

## Deferred until the Core Box is scanned

Not open for now. Leave this as it is and don't raise it again until the Core Box content is in `resources/scans/`.

- **Core Box Burnham variant** (REQ-CTM-21): The rule refers to a Burnham Status card, but no Crew deck with that card is in the content yet. Not implemented.

## Rulings made while implementing the Crew decks

Each is implemented as described. Confirm, or say which to change.

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

Made while writing the code. Each is implemented as described. Confirm, or say which to change.

- **The two opponent entries** (cb-khan): at most one of them may use a trait that is also printed on the board. This is what the rulebook's Soval example needs: Vulcan plus Ambassador or Telepath, never Ambassador and Telepath together.
- **Devastated Ceti Alpha V** (2KHA02B): its ACTIVATION can be used with an Away Team there: it draws nothing but exhausts the card, which Marla McGivers looks for.
- **Marla McGivers** (2KHA13): she counts herself as a Starfleet card in play for her PLAY.
- **Ceti Eel** (2KHA08): offered only while the opponent has a Duty Officer. If the attack is ignored, no Duty Officer is dismissed and no Away Teams are sent; the card still returns to the Development pile and the opponent may still draw.
- **Cpt. Terrell** (2KHA06): "at no Dilithium/Latinum/Incident cost" keeps conditions such as "have Marla McGivers logged". Terrell in the Staging Area is himself a Mind Control Person in play.
- **Revenge Is a Dish Best Served Cold** (2KHA10): "mark one trait of it" reads the card's own traits; a Wildcard does not count there. If the second PLAY's attack is ignored, the card is not given and a chosen Incident is returned (KW-GIVE-04).
- **Khan's three Incidents** (2KHA19 to 2KHA21): the Glory and the opponent's draw depend only on the revealed card, not on whether the attack was ignored. In Cadet Training the card is returned and you gain 1 Glory, as when an Incident is given to the virtual opponent.
- **Genesis Device** (2KHA11): "mark any one trait" may fill an opponent entry with any trait allowed for it. A destroyed neutral Location is replaced from the Location deck.
- **S.S. Botany Bay** (2KHA16): an effect that offers Ships to warp may still list it; choosing it does nothing.
- **Marooned for All Eternity** (cb-khan): the opponent chooses one of their Duty Officers or beamed Persons; a Person in their Staging Area cannot be chosen.
- **Wrathful Khan** (2KHA01B): a Best Focus icon counts as one Focus icon for his ENDGAME.

## Rulings made while implementing the Khan Bot

Made while writing the code. Each is implemented as described. Confirm, or say which to change.

- **Marking** (REQ-CD-KHN-11): the Bot marks when it gains, takes or takes control of any card, Incidents and Encounters included. For an Opponent's Captain entry it uses the first fitting trait in the printed order of your Captain's traits.
- **Value**: the 3 extra for a card with an unmarked trait applies to every Bot choice by value, not only to gains.
- **KHAN IN EXILE**: a card matches a row by trait or by suit; a Wildcard matches only the Augment row; an Encounter matches no row. A Location played from the Bot deck stays in the Staging Area and is discarded at Clean-up. "Drawn from the Supplement deck" includes the card put on a new Bot deck at a reshuffle.
- **Reshuffle**: the top Supplement card goes on the new Bot deck although Khan's Captain says he does not enlist, because the Bot ignores card text (REQ-SOLO-80).
- **Mind Control row**: the Bot gains 2 Glory whenever you dismiss no Duty Officer, also when you cancel the attack.
- **Attack row**: "you log this card" puts *Revenge Is a Dish Best Served Cold* into your Log and is part of the attack. If you cancel the attack, it stays in the Bot's Staging Area.
- **"Take an Incident to gain a Person"** does both. **"Gain an unmarked > Person / Cargo / Ship / Ally from the Junk"** takes any unmarked Junk card first.
- **Khan's three Incidents, SURPRISE** (2KHA19 to 2KHA21): only putting the card in your Discard pile is the attack; you draw either way.
- **Two Dimensional Thinking, SURPRISE** (2KHA22): the Bot's Captain counts as in play, so the Khan Bot always returns it.
- **Khan's ATTACK BOOST bonuses** are attacks on the Bot, which cannot cancel them.

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

## Core Box and promo set 1

From writing the specs (plans/base-game.md Step 2). None of these cards has code yet. Each has a default, which is what the spec says; confirm or change before the step that writes the card.

Questions about a card:

- **Mirok** (1PER15): the set code is printed with a dagger (†) and a 2025 copyright, unlike every other Core Box card, and no *To Boldly Go* card replaces him. Default: the mark has no effect.
- **Xindi-Reptilian Battleship** (1SHI13, 2SHI13): the Core Box card spells it "Reptilian"; the *To Boldly Go* spec says "Reptillian". Default: keep the *To Boldly Go* spelling on both until you check the card.
- **Sha Ka Ree** (1ENC07): implemented as a card that goes among your controlled Locations when played. Ships can warp to it, Away Teams can be sent to it, it counts as a controlled Location, and playing it counts as taking control. Confirm.
- **Conspiracy** (1DIR01): it cannot be discarded, so it stays in a human's hand at Clean-up. Default: it counts as a card in hand for the refill.
- **Inert Dilithium** (1BUR02):
  - Default: the 1 Dilithium at setup starts in Burnham's supply, not on the card.
  - Default: Dilithium on the card does not count for "for every N Dilithium you have" (Theta Zeta, Coridan) and cannot be stolen.
- **Weytahn** (1SHR12): "If there are no Away Team here, dismiss this card." Default: only the owner's Away Teams count.
- **Orb of Prophecy and Change** (1SIS04): "Refresh a Bajoran to draw a card." Default: offered only when an exhausted Bajoran is in play.
- **Halkan Council** (1ALL07): its CLEAN-UP logs it "if you have an Attack in play". Default: mandatory, checked while the card is still in the Staging Area.
- **Wesley Crusher** (0ENC01): the two Skill icons are read as [Any Skill]; they are small in the scan. Check the card.
- **Quark** (1SIS24): "after resolving an operation with a [Latinum] cost". Default: only Latinum paid as a cost counts, not Latinum spent by a "you may spend" effect.
- **"Discovery"** on the Picard and Burnham boards. Default: it means Encounter.
- **Founding the Federation** (Shran's mission): Default: the Human and the three other traits come from four different cards.

Rulings made while writing the Market cards (Step 5). Each is implemented as described; confirm or say which to change.

- **Ferengi Wine** (1CAR04): it counts itself as a Ferengi in play, since the text does not say "excluding this card".
- **Laris** (1PER11): "a Resupply operation you have already resolved this turn" means the RESUPPLY of a card before her in the fixed order the engine resolves them: Captain, Status, Fleet, Locations, then Duty Officers in order.
- **Laris** (1PER11): her Activation is offered only when a Captain, Cargo, Ship or Location of yours is exhausted.
- **B-4** (1PER05): you gain the Dilithium for your Log even when the opponent ignores the attack; only their Incident is skipped.
- **Mek'leth** (1CAR09): the opponent's whole hand is named in the log, then you may pick one Attack from it. Against the Bot you say whether it succeeded.
- **Tachyon Detection Grid** (1CAR13): a Cloak in the opponent's Staging Area cannot be chosen. In Cadet Training you gain the Glory.
- **Mirok** (1PER15): he may be promoted whether or not a Cloak was logged.
- **Admiral Pressman** (1PER03): "Free play an Attack" is mandatory when you have one in hand.
- **Captain Dorg** (1PER07): a Klingon in your Staging Area cannot pay his first Reaction, since the Staging Area cannot be dismissed from (KW-DSM-04).
- **U.S.S. Reliant** (1SHI11): in Cadet Training the virtual opponent counts as having at most 1 Ship.

Rulings made while writing the Locations, Encounters and promo cards (Step 6):

- **Amargosa Observatory** (1LOC01): when it is logged, you choose one Location you control or a neutral one, and every Ship of yours that can warp goes there.
- **Iconian Gateway** (1ENC04): you choose how many Away Teams to send, 0 to 3, then the one Location.
- **Derna** (1LOC09): "return an Incident" is from your hand; with none, you still gain the Dilithium.
- **Regula I** (1LOC15): the CONTROL is one choice: find a Scientist, or pay 3 Dilithium to scan for one, or neither.
- **Wesley Crusher** (0ENC01): the PASSIVE works only while he is in a table position, in practice as a Duty Officer. It covers Activations and Reactions of staged Persons, not their PASSIVEs.
- **U.S.S. Enterprise-B** (0SHI01): when the weekday is not known (a game saved before weekdays were recorded) it is not Tuesday.
- **Whale Probe Incursion** (0INC02): recalling your own Ship is mandatory when you have one; without a Creature the card stays yours and is discarded at Clean-up.

Rulings made while writing Picard's deck (Step 7):

- **Jean-Luc Picard** (1PIC01): the gained Ally is beamed from wherever it went (top of your deck or your Discard pile).
- **Seek Out New Life** (mission): each Alien card and each Transcendent card is one species of its own; its other Species traits are not counted as well. Wildcards are not counted.
- **Data** (1PIC12): each point from his Activation may go on a different track.
- **Tamarians** (1PIC04): the discards are chosen from your whole hand after drawing, not only from the 3 cards drawn.
- **Starbase 74** (1PIC07): the found Person can be free played only if it ended up in your hand, which a find always does.
- **Type 7 Shuttlecraft** (1PIC14): with no Ship at a Location, its first PLAY sends no Away Team but may still be put back on your deck.
- **Worf** (1PIC23): his Activation is offered only when an opponent Away Team shares a Location with one of yours. In Cadet Training that is any neutral Location where you have one.

Rulings made while writing Shran's deck (Step 8):

- **Founding the Federation** (mission): the Ship card itself counts as a card "on the same Ship" (REQ-MS-03), so the Andorian *Kumari* supplies Andorian. The Human and the three traits still come from four different cards.
- **Tarah, Korax** ("discard the top card of your opponent's Draw deck"): discarding it is the attack part; the Glory is gained either way. In Cadet Training there is no deck, so only the Glory is gained.
- **Ambassador Thoris** (1SHR09): the opponent chooses whether to return one. The Bot declines. You gain Glory for theirs as well as yours.
- **Imperial Pride** (1SHR16): "shares no traits with your Captain" compares printed and "treated as" traits of the logged Location.
- **Talas** (1SHR20): the opponent's Captain cannot be chosen, nor a card in their Staging Area.
- **Tarah** (1SHR21): her Activation refreshes a Ship and a Location if either is exhausted; it can be used with neither.
- **Aenar** (1SHR03): the cards logged or discarded must be among the 3 just drawn.

Rulings made while writing Koloth's deck (Step 9):

- **Sword of Kahless** (1KOL04): dismissing a Klingon Duty Officer for 4 Glory is optional; the card is logged either way.
- **Kang** (1KOL07): his first PLAY gains the Glory even with no Incident to return. His Reaction does not trigger itself, since he is exhausted by it.
- **Good Day to Die** (1KOL17): with fewer than two deployed Ships the second sentence does nothing, and with two you may still decline it.
- **Korax** (1KOL22): at Clean-up the hand size rises by 1 for each unspent Action, and you are asked once whether to take that many Glory.
- **Korax** (1KOL22): his Activation is offered only when the *Gr'oth* or another Klingon Ship is exhausted.
- **Boreth** (1KOL05): its ENDGAME counts every Skill icon on your cards in play that are not beamed, your Captain's and Boreth's own included.
- **Sabotage** (mission): you choose whether to attack; if you do, the opponent may ignore it.

Rulings made while writing Sela's deck (Step 10):

- **Sela** (1SEL01): she is paid once per attack, also when the opponent ignores it, and in Cadet Training. Her Activation needs *Infiltrate* or *Conquer* in hand, matched by name.
- **Scimitar** (1SEL07): the Romulan is found and destroyed even when you cannot then beam a card to *Remus*; the Ship is deployed only if both happened. *Remus* must be under your control.
- **Scimitar** (1SEL07): the logged Location goes to its owner's Log. Glory counts its Skill icons as its owner had them. In Cadet Training it gains 1 Glory.
- **Donatra** (1SEL04): for each of the 3 drawn cards you choose to pay 1 Dilithium to keep it, or it is discarded.
- **Shinzon** (1SEL06): his RESUPPLY must log a Romulan when one is in your hand or Discard pile.
- **Tomalak, T'Rul** ("discard a card to draw X from your Discard pile"): the card just discarded cannot be the one drawn.
- **Remans** (1SEL24): you choose between logging the card and letting the opponent draw.
- **The Duras Plot** (mission): you choose which one Cloak to dismiss; a Cloak in your Staging Area cannot be chosen.
- **Romulan Might** (mission): enlisting a Development still costs its development cost.

Rulings made while writing Sisko's deck (Step 11):

- **Taking control** (all decks): playing a Crew Location from hand counts as taking control of a Location (KW-TC-02). So *Benjamin Sisko* gains 2 Dilithium for *The Wormhole* and *Starbase 375*, and the older cards that react to taking control (*Wajahut*, *Chancellor Gowron*, *Proconsul Neral*, *Ambassador Kamarag*) now react to it too. Confirm.
- **Benjamin Sisko** (1SIS01): his Activation needs a Location with Starfleet or Starbase. *Deep Space 9* is a Ship, so it does not count; *Bajor* has neither trait.
- **Self-Replicating Mines** (1SIS06): the PASSIVE is not optional. The first attack against you while the card is deployed is ignored and the card is logged, before *Worf, Son of Mogh* or any other Reaction is offered.
- **Worf, Son of Mogh** (1SIS10): his Activation gains the Glory even when the attack is ignored. It needs an opponent Away Team at a neutral Location.
- **Garak** (1SIS09): only "dismiss a Duty Officer" is the attack. You draw the card even when the attack is ignored or the opponent has no Duty Officer.
- **Orb of Prophecy and Change** (1SIS04): "refresh a Bajoran" needs an exhausted Bajoran. The discount is 1 Dilithium and 1 Latinum, each only if the cost has it.
- **A Call to Arms** (mission): for each Starbase in play you choose whether it takes off 1 Dilithium or 1 Latinum. *Deep Space 9* counts.
- **Miles O'Brien** (1SIS13): "draw a Ship from your Discard pile and free play it" plays that Ship; if it cannot be played it stays in hand.
- **Quark** (1SIS24): his Reaction is for Latinum that a cost asks for, even when Glory paid for it. Latinum spent by a "you may spend" effect, and development costs, do not count.
- **Kira Nerys** (1SIS23): the Cardassian or Dominion card must be in the opponent's Control Area or Fleet; not their Captain and not a card in their Staging Area.
- **U.S.S. Defiant** (1SIS15): the attack is made only when the opponent has a Ship at the Location it warped to.
- **Miles O'Brien, and the other "cannot be promoted" cards:** a promote effect can still pick him, and then does nothing.

Questions about a Bot row:

- **Picard, Klingon row:** "If able, you remove an Away Team." Default: from the Location the Bot just sent to; if you have none there, from a Location of your choice.
- **Sela, Shady row:** "take control of the neutral Location with most Bot tokens (minimum 1)". Default: the Bot takes it without having secured it, and your tokens there earn you Glory as usual.
- **Sela, Klingon row:** "either you dismiss a Ship OR resolve the top card of the Bot deck". Default: your choice; with no Ship to dismiss, the Bot resolves the top card.

Reprints: the 45 Core Box cards that *To Boldly Go* reprints were matched by name, and their specs are copies of the *To Boldly Go* specs. I compared the text of each pair on screen but not word for word, so small wording differences on the older printing may be unrecorded. The reprint shares the newer card's code either way.

## Gaps in the CLAUDE.md action list

The Core Box needs these additions. Each is a general option on an existing action or a new registry, not a new action, except where noted. They are written in the step that first needs them.

| Need | Cards | Proposed |
|---|---|---|
| Recrystallize: move Dilithium from Inert Dilithium to the supply | Jett Reno, Sylvia Tilly, Paul Stamets, Theta Zeta, Burnham's mission | `MOVE_RESOURCES` with the card as source (`recrystallize(n)`), and a registry that redirects the owner's Dilithium gains onto a Status card |
| Log a Status card | Theta Zeta | `LOG` reaches Status cards |
| An attack that dismisses a Duty Officer can be ignored by a specific Reaction | Book's Ship | `attack(dismisses_duty_officer=True)`, as `removes_away_teams` |
| "You cannot send Away Teams here" | Theta Zeta | a registry read by `away_targets` |
| Which RESUPPLY operations resolved this turn | Laris | engine bookkeeping; `DUPLICATE` with `kind="RESUPPLY"` already exists |
| The Bot gains "the Market card with the most Dilithium, then most Glory" | Burnham Bot | `gain_most(resource)` generalising `gain_most_glory` |
