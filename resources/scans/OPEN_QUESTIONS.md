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

- **Sakonna** (1PER21): her second PLAY needs "a Ship at the Badlands". No Location named Badlands is in any scanned set. Default: the PLAY can never be used. Is a card missing from the scans?
- **Mirok** (1PER15): the set code is printed with a dagger (†) and a 2025 copyright, unlike every other Core Box card, and no *To Boldly Go* card replaces him. Default: the mark has no effect.
- **Xindi-Reptilian Battleship** (1SHI13, 2SHI13): the Core Box card spells it "Reptilian"; the *To Boldly Go* spec says "Reptillian". Default: keep the *To Boldly Go* spelling on both until you check the card.
- **Sha Ka Ree** (1ENC07): "considered a Location for all purposes" and "deploying it counts as taking control". Default: Ships can warp to it and Away Teams can be sent to it, as to a controlled Location; it stays in the Fleet Area.
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
| Draw the bottom card of your deck | Boreth | `draw(bottom=True)` |
| Discard the top card of the opponent's Draw deck | Tarah, Korax, Shran Bot | `discard_from_deck(player=opponent)`, an attack part |
| Resolve the top card of the Bot deck from a SURPRISE | Flight Training Accident | `RESOLVE_CARD` available to SURPRISE operations, as `CONTINUE_RESOLUTION` now is |
| Log a Status card | Theta Zeta | `LOG` reaches Status cards |
| "Considered a Location" | Sha Ka Ree | an `ALSO_SUIT`-style entry, and a `take_control` event on deploy |
| Enlist with a discount of several resources | Orb of Prophecy and Change, Sisko's mission | `enlist_development(discount=n)` or a per-resource discount |
| An attack that dismisses a Duty Officer can be ignored by a specific Reaction | Book's Ship | `attack(dismisses_duty_officer=True)`, as `removes_away_teams` |
| Use another card's Activations and Reactions | Wesley Crusher | a registry like `@granted_play` for ACTIVATION and REACTION |
| Ignore opponent Ships for every Away Team sent | Phasing Cloak | a registry read by `away_targets` |
| "You cannot send Away Teams here" | Theta Zeta | a registry read by `away_targets` |
| Which RESUPPLY operations resolved this turn | Laris | engine bookkeeping; `DUPLICATE` with `kind="RESUPPLY"` already exists |
| "After resolving an operation with a Latinum cost" | Quark | a new event, `operation_resolved`, carrying what the cost paid |
| "After attacking your opponent" | Sela | the existing `attacked` event, seen from the attacker's side |
| The weekday | U.S.S. Enterprise-B | the server stores the weekday with each command; `ctx.weekday()` reads it |
| The Bot gains "the Market card with the most Dilithium, then most Glory" | Burnham Bot | `gain_most(resource)` generalising `gain_most_glory` |
