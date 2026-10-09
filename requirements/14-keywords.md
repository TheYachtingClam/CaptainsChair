# 14 – Keywords in Detail (Rules Engine Primitives)

Source: Rulebook pp. 28–33. These entries **override** the general rules where they conflict (REQ-OV-10).

Each keyword below must be a reusable engine primitive that card scripts call. Entries are alphabetical, as in the rulebook.

## Areas

- **KW-AREAS** For areas of the table, see *In Play / From Play*.

## Another / All other

- **KW-ANOTHER-01** "Another [suit or trait the card itself has]" means one of that thing, **excluding** this card.
- **KW-ANOTHER-02** "All other" means everything matching, except this card. "Each [X] (excluding this card)" means the same.
- **KW-ANOTHER-03** Exclusions are always stated explicitly. If a card does not say, the card **itself is included** in any condition it matches.

## Attacked / Negative effect

- **KW-ATK-01** A player is **attacked** when the opponent resolves an operation preceded by ATTACK.
- **KW-ATK-02** Every part of that operation that targets the attacked player is its **negative effect**. That includes their hand, cards, play area and resources, giving them Incidents, and forcing them to act.
- **KW-ATK-03** If a card lets the player ignore the negative effect, they ignore all those parts. The attack still counts as having happened for other effects. The attacker still resolves the parts that do not target the defender.

## Beam

- **KW-BEAM-01** Take a card from hand, unless another source is specified. Place it faceup under the target card, usually a Ship, so only its suit and trait icons show. The card is now **beamed**.
- **KW-BEAM-01a** Beaming never takes a card from the top of the Draw deck, or from any other source, unless the effect names that source. Example: Jackabog beams a Ship it has just gained.
- **KW-BEAM-02** A card can hold any number of beamed cards. An effect may limit which suits can be beamed.
- **KW-BEAM-03** A Location can never be beamed to another card. A Ship can be beamed to another Ship.
- **KW-BEAM-04** A beamed card is in play. Its operations and Skill icons are not.
- **KW-BEAM-05** A card beamed to a Ship is "on" that Ship. A card beamed to a Location is "at" that Location, and that Location is the beamed card's location.
- **KW-BEAM-06** If the host card is dismissed, recalled or logged, the beamed cards suffer the same effect.
- **KW-BEAM-07** Beamed cards are public.

## Considered (another suit)

- **KW-CONS-01** A SPECIAL operation "This card is considered (another suit) for all purposes" is always active for non-Bot players. The card is **dual-suited**.
- **KW-CONS-02** Effects that target either the printed suit or the extra suit can target the card.
- **KW-CONS-03** A card considered a Ship has a Ship token that works like any Ship's token.

## Deploy

- **KW-DEP-01** Only Ships, or cards with the Ongoing trait, can be deployed. Ongoing can appear on Cargo, Ally, Directive or Encounter cards.
- **KW-DEP-02** Move the in-play card from the Staging Area to the Fleet Area. For a Ship, also place its Ship token on the card. Table operations are available immediately.
- **KW-DEP-03** If a Duplicate effect would deploy a card that is neither a Ship nor Ongoing, nothing happens.

## Destroy

- **KW-DES-01** A destroyed card is removed permanently and **returned to the box**. The player no longer owns it, so it does not score.
- **KW-DES-02** Cards beamed to a destroyed card are also destroyed.
- **KW-DES-03** If a Location is destroyed, Ships there are dismissed and Away Teams return to their owners' Captains.
- **KW-DES-04** Resource tokens on the destroyed card return to the supply.

## Discard

- **KW-DIS-01** Choose a card from **hand** that matches any restriction and put it in the Discard pile.
- **KW-DIS-02** Discard never affects cards in play. That is *dismiss*.

## Dismiss

- **KW-DSM-01** Move a card from play to its owner's Discard pile. Cards beamed to it go to the Discard pile too.
- **KW-DSM-02** If the dismissed card was itself beamed to another card, the host card is unaffected.
- **KW-DSM-03** Resource tokens on the dismissed card return to the supply.
- **KW-DSM-04** Cards in the Staging Area cannot be dismissed.
- **KW-DSM-05** A Location cannot be dismissed unless the Location's own text says so.
- **KW-DSM-06** An Action token on a dismissed card goes beside the Discard pile. It stays spent and is only a reminder.
- **KW-DSM-07** Dismissing a Ship returns its token to the supply and dismisses its beamed cards.
- **KW-DSM-08** If an ATTACK dismisses an opponent's in-play card, the card goes to **that opponent's** Discard pile.

## Draw / Draw from Discard

- **KW-DRW-01** Draw takes the top card of the Draw deck into hand. There is no hand limit.
- **KW-DRW-02** If the deck is empty when drawing:
  1. Reshuffle the Discard pile into a new Draw deck.
  2. Enlist a Reserve if possible. Otherwise, the player may pay to enlist a Development.
  3. Keep drawing. The enlisted card comes next.
- **KW-DRW-03** "Draw from your Discard pile" lets the player search the whole faceup Discard pile and take a card that matches.
- **KW-DRW-04** Draw never touches cards in play. That is *recall*.

## Drone, Assimilate

- **KW-DRONE-01** These keywords have no defined meaning yet. The engine should reserve them for future expansions.

## Duplicate

- **KW-DUP-01** Choose a card of the given suits from one of the named positions: Market, Discard pile or the player's Log. Resolve one of its listed operations, usually a PLAY operation.
- **KW-DUP-02** No extra action is spent, even if the copied operation has an action cost.
- **KW-DUP-03** Specialty requirements of the copied effect still apply.
- **KW-DUP-04** If the copied operation mentions its own card ("this card", e.g. "Log this card"), apply that to the **duplicating** card where possible. Examples:
  - *Orb of Time* copying a self-logging *Denobulans* logs the *Orb of Time*.
  - *Vadic's Splinter Group* copying "Deploy this card" does nothing, because the Splinter Group is neither Ship nor Ongoing.
- **KW-DUP-05 No duplicate duplicates.** Duplicating a Duplicate effect does nothing. For example, *Laas* copying *Orb of Time* only allows a recall.

## Enlist a Development

- **KW-ENDEV-01** Pay the development cost of any card in the Development pile and put that card on **top** of the Draw deck. The pile has no order; the player may look through it.
- **KW-ENDEV-02** Normally allowed only when reshuffling with an empty Reserve deck. It is also allowed whenever an effect explicitly permits it, even with Reserves left.
- **KW-ENDEV-03** The whole development cost must be paid.
- **KW-ENDEV-04 Enlist for free** ignores the whole development cost: resources, side effects and preconditions.
- **KW-ENDEV-05** Apart from enlisting, the Development pile cannot be used unless an effect says so. Cards still there do **not** score.

## Enlist a Reserve

- **KW-ENRES-01** Move the top Reserve card, unseen, to the top of the Draw deck.
- **KW-ENRES-02** With an empty Reserve deck this does nothing. It cannot become a Development enlist.
- **KW-ENRES-03** Cards left in the Reserve deck do not score.

## Exhaust

- **KW-EXH-01** Rotate an in-play card sideways, as though an ACTIVATION or REACTION had been used. This can be a Fleet Area card, Location Area card, Duty Officer or Captain.
- **KW-EXH-02** Its ACTIVATION and REACTION operations stay unusable until the end of the owner's Clean-up, unless an effect refreshes it.
- **KW-EXH-03** Exhausting is a **cost**. If there is no card to exhaust, the operation cannot be resolved.
- **KW-EXH-04** An exhausted card cannot be exhausted again. An effect that offers "exhaust it" as an option cannot use that option on an already exhausted card.

## Find [name / suit / trait / icon]

- **KW-FIND-01** Search the hand, Discard pile, Draw deck and Reserve deck for a card that matches. Put it into hand if it is not already there.
- **KW-FIND-02** The player need not take the first match. They may keep searching.
- **KW-FIND-03** Some effects restrict where to search. The most common is "except in your Reserve deck".
- **KW-FIND-04** With several criteria, the player may look at every card that meets any of them and choose one.
- **KW-FIND-05** Finding by trait also allows a Wildcard card. Finding by Skill or Focus also allows an Any Skill or a Best Focus card.
- **KW-FIND-06** Afterwards, shuffle any facedown deck that was searched: the Draw deck and the Reserve deck.

## Force

- **KW-FORCE-01** "Force your opponent to X" means the opponent resolves X and makes every choice inside it.
  - "Dismiss an opponent's Ship": the active player chooses which.
  - "Force your opponent to dismiss a Ship": the opponent chooses.
- **KW-FORCE-02** Ownership never changes unless stated. "Log an opponent-controlled Location" puts it in the **opponent's** Log.
- **KW-FORCE-03** For a forced "either A or B", the opponent must choose one they can fully resolve if possible. If neither can be resolved, they ignore it.

## Free play [suit / trait / Incident / named card]

- **KW-FREE-01** Choose a matching card from hand, unless stated otherwise, and play it as usual. If the chosen PLAY operation has an action cost, no action is spent.
- **KW-FREE-02** Free play does not waive any other costs. It gives no extra action if the operation had no action cost.

## Gain [a card]

- **KW-GAIN-01 Gain [suit].**
  - Choose the faceup Market card of that suit, or the unseen top card of its deck.
  - Look at it, then place it on top of the Draw deck or in the Discard pile, unless the effect says otherwise.
  - If several suits are listed, choose one.
  - If no cards of that suit remain, nothing happens.
- **KW-GAIN-02 Gain [trait].**
  - Take a faceup Market card of any suit that has the trait.
  - Place it on the Draw deck or in the Discard pile.
  - If no faceup card has the trait, nothing happens.
- **KW-GAIN-03** Taking a faceup Market card also takes its resource tokens. Refill the slot from the matching deck; leave it empty if that deck is empty.
- **KW-GAIN-04** "Gain from the Junk" lets the player search the Junk pile for a card of the named suit(s).

## Gain resources

- **KW-GRES-01** Move the tokens into the player's resource pool.
  - Latinum and Dilithium come from the supply.
  - Glory comes from the topmost Stardate card, or from the supply after a Resolution.
- **KW-GRES-02** If more Glory is due than the top Stardate holds:
  1. Take everything there, which empties it.
  2. Give that card to the inactive player.
  3. Fill the new top card with its printed Glory and keep taking.
  4. If it was the last Stardate card, leave it in place and take the rest from the supply.
- **KW-GRES-03** "Gain [resource] from [card]" takes from that card only. If the card has none, the player gets nothing.
- **KW-GRES-04** Resources are unlimited.

## Gain / Spend an Action

- **KW-ACT-01** Gaining an action adds one more available Action token from the supply to the personal pool, as a 4th, 5th and so on.
- **KW-ACT-02** Gained actions last only for the current turn. The pool resets to 3 during Clean-up.
- **KW-ACT-03** To spend an action, for an operation with the action icon or an explicit cost, flip an available token to spent and place it on the card. With no available token, the operation cannot be used.

## Give [a card]

- **KW-GIVE-01** Move the card, usually an Incident, from the player's hand, unless stated otherwise, into the **opponent's hand**.
- **KW-GIVE-02** If the player has no such card, nothing happens. The opponent does not draw from the Incident deck instead.
- **KW-GIVE-03** Giving an Incident is **not** returning one. It **does** count as the opponent taking one. Some Passive and Reaction triggers depend on this.
- **KW-GIVE-04** When an Incident is given as an attack and the attack is ignored, the Incident is returned to the Incident deck instead (ruling). In solo mode this also covers a Bot row's "you take this card".

## Helmet / Wearing a helmet

- **KW-HELM-01** Some effects beam a card with the Helmet trait to the Duty Officer. That Person is then "wearing" it, which usually unlocks a stronger effect. This relates to Rebner's Pakleds.
- **KW-HELM-02** A Duty Officer can wear only one Helmet.
- **KW-HELM-03** If the Duty Officer is dismissed, recalled or logged, the Helmet goes with them.

## In Play / From Play

- **KW-INPLAY-01** In play for a player:
  - Location Area: controlled Locations.
  - Fleet Area: deployed Ships and Ongoing cards.
  - Duty Officer(s).
  - Captain, and any Status cards.
  - Staging Area. Table operations there are unavailable, and these cards go to the Discard pile in Clean-up.
  - Cards beamed to a Ship or Location. Their table operations are covered, and they are dismissed if they help complete a mission.
- **KW-INPLAY-02** **Not** in play: hand, Draw deck, Discard pile, Reserve deck, Development pile, and the Captain's Log.
- **KW-INPLAY-03** The opponent's cards are in play for the opponent's effects, not for the player's own effects, unless stated.

## Junk a card (from the Market)

- **KW-JUNK-01** Choose a faceup Market card and put it in the Junk pile. Refill from the matching deck, or leave the slot empty if that deck is empty.
- **KW-JUNK-02** A player may never junk a card that has resource tokens on it. Stardate wipes can still remove it.
- **KW-JUNK-03** Junking always targets the Market unless stated. Neutral Zone cards never go to the Junk.
- **KW-JUNK-04** The Junk pile is out of play. Its cards cannot be used unless an effect allows it.

## Log

- **KW-LOG-01** Every card under the Captain is in the Captain's Log. To log a card, tuck it under the Captain. Cards beamed to it are logged too.
- **KW-LOG-02** If no source is given, the logged card comes from hand.
- **KW-LOG-03** Resource tokens on it return to the supply.
- **KW-LOG-04** Logging a Location dismisses the Ships there and returns Away Teams to their Captains.
- **KW-LOG-05** Logged cards are out of play and unusable unless an effect allows it. They still **score VP**.
- **KW-LOG-06** The owner may look at their own Log at any time. Per the developers' errata, the opponent may ask about its contents and the owner must answer.
  - Online ruling: both players can open either Log by clicking it. See [11-logging-and-hidden-information.md](11-logging-and-hidden-information.md) §3.
- **KW-LOG-07** "Log this card" in a PLAY operation moves the card from the Staging Area to the Log. Its Action token goes beside the Captain as a reminder.
- **KW-LOG-08** If an ATTACK logs an opponent's card, it goes into **the opponent's** Log.

## Market

- **KW-MKT-01** "The Market" always means the four faceup Market cards, or fewer when a deck has run out.

## Move resources

- **KW-MOVE-01** Move tokens from the player's pool onto a named card in the Market or in play.
- **KW-MOVE-02** This is not spending, so Glory cannot substitute for Dilithium or Latinum.

## Place resources

- **KW-PLACE-01** Take tokens from the supply, or Glory from the Stardate card if able, and put them on the named card.
- **KW-PLACE-02** Resources on the player's cards at scoring time are not theirs unless stated.

## Promote (a Person to Duty Officer)

- **KW-PROM-01** Take a Person from the named position (hand, Staging Area or Discard pile) and put it in a Duty Officer slot. Its table operations are available immediately.
- **KW-PROM-02** A PLAY operation that promotes its own card moves it immediately; it does not stay in the Staging Area.
- **KW-PROM-03** An Action token on the promoted card moves with it as a reminder. It does not block the card's Reaction or Activation, even one that costs another action.
- **KW-PROM-04 Duty Officer limit.** The limit is normally **1**; effects can raise it.
  - Whenever the player has more Duty Officers than the limit, they must dismiss one.
  - An effect granting extra Duty Officers of a certain kind, when it sits on a Duty Officer, applies to the **others**. That Duty Officer cannot count as its own "additional" officer.
- **KW-PROM-05** A player cannot voluntarily dismiss their only Duty Officer. It leaves only when an effect says so, or when promoting a replacement.
- **KW-PROM-06** If a Duplicate effect would promote a non-Person, nothing happens.
- **KW-PROM-07** With several Duty Officers, the Location Area layout shifts to make room in the top row.

## Put a card (somewhere)

- **KW-PUT-01** Choose a matching card from hand, unless stated otherwise, and place it where the effect says: the top of the deck, the Staging Area, and so on.

## Put into play

- **KW-PIP-01** A card is **put into play** when:
  - it is played, immediately after one of its PLAY operations resolves;
  - a neutral Location is taken under control, immediately before its CONTROL operation resolves;
  - a Person is promoted from hand or Discard pile;
  - it is beamed from hand or Discard pile;
  - an effect explicitly puts it into the Staging Area.
- **KW-PIP-02** A trait or suit is put into play when a card that has it is put into play.

## Reaction operations

- **KW-REA-01** Reactions are optional. Once one starts resolving, its effects are mandatory unless stated.
- **KW-REA-02** A Reaction can **interrupt** another operation at the moment its condition is met. The interrupted operation resumes afterwards. The engine needs an interrupt / trigger stack.
- **KW-REA-03** If a card's own PLAY or CONTROL operation meets an "after [X]" condition of a Reaction on that same card, and the card was deployed or taken under control by that operation, the Reaction can be used at once.
- **KW-REA-04** When several Reactions share a trigger, the player may resolve any number of them in any order.
- **KW-REA-06** Ordering across both players, "when … would" versus "after" timing, and nested triggers follow REQ-AS-26 to REQ-AS-33 in [06-action-step.md](06-action-step.md).
- **KW-REA-05** A Reaction "when you gain a [card]" also triggers on a card gained by scanning.

## Recall

- **KW-REC-01** Return a card from play to hand. It can be played again, even the same turn.
- **KW-REC-02** Cards beamed to it are recalled too. If the recalled card was itself beamed somewhere, the host card is unaffected.
- **KW-REC-03** Resource tokens on it return to the supply.
- **KW-REC-04** A Location cannot be recalled unless its own text says so.
- **KW-REC-05** Its Action token is set aside and the action is **not** regained. If the card is played again with another action, both tokens may sit on it as reminders.

## Recrystallize

- **KW-RECRY-01** "Recrystallize N [Dilithium]" belongs to Burnham's deck in the Core Box. Move up to N Dilithium from her *Inert Dilithium* Status card to her supply (REQ-CORE-31).
- **KW-RECRY-02** It is moving, not gaining: effects that trigger on gaining Dilithium do not trigger, and the Dilithium is not placed back on *Inert Dilithium*.
- **KW-RECRY-03** "Recrystallize all" moves everything on the card. With nothing on the card, or no *Inert Dilithium* in play, nothing happens.

## Refresh

- **KW-REF-01** Un-exhaust an in-play card so its ACTIVATION or REACTION can be used again this turn.
- **KW-REF-02** Any Action token on the card stays as a reminder and does not block use.

## Requires

- **KW-REQ-01** "Requires…" is a precondition, usually a Specialty level, sometimes a more complex condition.
- **KW-REQ-02** If it is not met, no part of the operation can resolve.
  - An unresolvable PLAY operation cannot be used to put the card into the Staging Area.
  - An unresolvable ACTIVATION cannot be used just to exhaust the card.

## Return an Incident

- **KW-RETI-01** Put the Incident facedown on the **bottom** of the Incident deck. It comes from hand unless stated otherwise.
- **KW-RETI-02** An Action token on it goes beside the Incident deck as a reminder.
- **KW-RETI-03** Cards in the Incident deck are out of play and cannot be used unless an effect allows it.

## Scan

- **KW-SCAN-01 Scan # of [suit].**
  - Look at the top # cards of that deck.
  - Gain one of them or the faceup Market card of that suit.
  - Put it on top of the Draw deck or in the Discard pile.
  - Put the unchosen cards on the bottom in any order.
- **KW-SCAN-02** If fewer than # cards remain, look at all of them. If the suit is exhausted in both Market and deck, nothing happens.
- **KW-SCAN-03** If several suits are listed, pick one. The choice cannot change after looking, and the other suits' faceup cards cannot be taken.
- **KW-SCAN-04 Scan including the Junk (suit).** After looking at # cards, the player may also search the whole Junk pile for that suit. They choose from the Junk, the Market or the # cards.
- **KW-SCAN-05 Scan for [trait / icon].**
  1. If any faceup Market card matches, gain one.
  2. Otherwise, pick a suit and reveal from its deck until a match appears. Gain it, then shuffle the other revealed cards back.
  3. If none is found, try the other suits.
  4. If nothing matches anywhere, gain **2 Glory** as compensation.
- **KW-SCAN-06** If several traits or icons are listed, pick one. The choice cannot change after starting on a Market deck.
- **KW-SCAN-07 Scan for, including the Junk.** After checking the Market and before the decks, the player may take a matching Junk card. Otherwise continue with the decks.
- **KW-SCAN-08** Taking a faceup Market card also takes its tokens. Then refill the slot, or leave it empty.

## Secured

- **KW-SEC-01** A neutral Location is secured by a player who has at least 3 tokens there in total (Away Teams plus Ships) **and** at least 2 more than the opponent.
- **KW-SEC-02** This matters for the Control Step and for effects that take control of a secured Location immediately.

## Send / Remove an Away Team

- **KW-SEND-01** Place or remove the stated number of Away Teams at a target Location, neutral or controlled.
- **KW-SEND-02** No Ship needs to be present unless the effect requires one.
- **KW-SEND-03** An Away Team cannot be placed at a Location where the opponent has **more** Ship tokens than the player.
- **KW-SEND-04** If the pool is empty, the player may move Away Teams from other cards.
- **KW-SEND-05** Away Teams removed for any reason, such as a logged Location or an attack, return to the personal pool on the Captain. The total number of Away Teams never decreases during play.

## Spend resources

- **KW-SPEND-01** Return the stated tokens from the resource pool to the supply. If they cannot be paid, the operation cannot be resolved.
- **KW-SPEND-02** Glory may substitute: 1 Glory counts as 1 Latinum or as 2 Dilithium, with no change given. There are no other conversions unless permitted.
- **KW-SPEND-03** "Spend all of your Dilithium/Latinum" may be paid with zero. The player is never forced to spend Glory for it.
- **KW-SPEND-04** "Spend [resources] from [card]" uses only that card's tokens. A player may never spend resources from cards unless told to.

## Steal [Dilithium / Latinum / Glory]

- **KW-STEAL-01** Take the stated resource from the opponent, up to what they have, possibly none. The thief cannot take a different type instead.
- **KW-STEAL-02** Stealing is not gaining. Reactions that trigger on gaining a resource do not trigger.

## Support (expansion)

- **KW-SUP-01** A SUPPORT operation lets a player put a Lower Decker card from hand into the Staging Area when its trigger happens during their Action Step, resolving only the SUPPORT effect. Full rules are in [21-expansion-second-contact.md](21-expansion-second-contact.md) §4.

## Take [a card]

- **KW-TAKE-01** Common forms are "Take an Incident" and "Take the top Encounter", or look at 2 Encounters and take one. The card goes **directly into hand**.
- **KW-TAKE-02** Reactions "when you gain a [card]" do **not** trigger on a taken card. An example is the solo *Reinforce* card.
- **KW-TAKE-03** If an ATTACK makes the opponent take an Incident, the top Incident goes into the opponent's hand.

## Take control

- **KW-TC-01** This always refers to a Location. For a neutral Location:
  1. Dismiss all Ships there and remove all Away Teams. The opponent gains 1 Glory per token removed or dismissed.
  2. Move the card to the Location Area.
  3. Resolve its CONTROL operation. This counts as putting the card into play for Reactions.
- **KW-TC-02** Neutral Locations are normally taken in the Control Step.
  - A Crew deck's own Locations are played from hand; their PLAY operation runs this procedure.
  - Some effects take control straight from the Location deck.

## Token

- **KW-TOKEN-01** "Token" means Away Team tokens and Ship tokens together.

## Treated as

- **KW-TREAT-01** A card "treated as [trait]" has that trait while the operation lasts.
- **KW-TREAT-02** "[Cards] are additionally treated as [trait]" keeps their printed traits and adds this one.
- **KW-TREAT-03** It does nothing to a card that already has the trait, because each card has each trait only once.
- **KW-TREAT-05** "Treated as [trait] for the remainder of your turn" (or "gains [trait] for the remainder of your turn") lasts until the turn ends, wherever the card goes in the meantime. Every effect that reads traits sees it, for example a Ship given Cloak by *Cloaking Device* can be warped by *Infiltrate*.
- **KW-TREAT-04** Some cards treat Skill icons of one colour as another. The original colour is then gone unless the card says otherwise. See [21-expansion-second-contact.md](21-expansion-second-contact.md) §6.

## Trigger [a Location's CONTROL operation]

- **KW-TRIG-01** Resolve the chosen Location's CONTROL operation, usually a controlled Location, as if control had just been taken.
- **KW-TRIG-02** It does **not** count as taking control for Reactions. Tokens and beamed cards there are unaffected.
- **KW-TRIG-03** If the Location has a PLAY operation, meaning it is not from the Location deck, still resolve only CONTROL.
- **KW-TRIG-04** Triggering CONTROL does not cost an action unless the text says so.

## Warp

- **KW-WARP-01** Place or move a deployed Ship's token to a controlled Location or to a Neutral Zone Location. It may move between Locations. There is no limit per Location.
- **KW-WARP-02** Staying in place is **not** warping.
- **KW-WARP-03** Once the token leaves the Ship card, it cannot return except by dismissing or recalling the Ship and deploying it again.
- **KW-WARP-04** A Ship at a Location, and all cards beamed to it, are "at" that Location. That Location is "that Ship's Location".
- **KW-WARP-05** The *Badlands* Location is mentioned but is not in this box. Reserve it for future content.
