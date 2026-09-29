# 21 – Expansion: Second Contact

Source: Second Contact expansion rulebook, [manual/expansion/](../manual/expansion/) pp. 1–6.

*Second Contact* is the first expansion. It needs the Core Box or *To Boldly Go* to play. It adds three Crew decks, the **SUPPORT** operation, the **Lower Decker** and **Crossover** traits, the **Reward pile**, and some common cards.

- **REQ-EXP-01** The expansion is an optional content pack. When creating a game, the host chooses whether to include it. The lobby shows which Crew decks need it.
- **REQ-EXP-02** Rules in this file add to the base rules. Where they conflict, this file wins for games that include the expansion.

## 1. Components

| Captain | Cards | Other | Ship tokens |
|---|---|---|---|
| Freeman | 25 | 1 Crew board | U.S.S. Carlsbad, U.S.S. Cerritos, Type 6A Shuttlecraft, A Fleet of 30 California-Class Ships |
| Pike | 26 | 1 Crew board | U.S.S. Enterprise |
| Riker | 25 | 1 Crew board | U.S.S. Titan, U.S.S. Zheng He |

Common cards:

| Type | Count |
|---|---|
| Market: Ally | 3 |
| Market: Cargo | 3 |
| Market: Person | 5 |
| Market: Ship | 2 |
| Location | 2 (including *Krulmuth-B*) |
| Reward: Person | 8 (for example *Ambassador Spock*) |
| Common Ship tokens | 2 |

Solo components: 6 Automated Command cards, including a Five Year Mission card for each new captain (see [22-solo-mode.md](22-solo-mode.md)).

## 2. Central setup changes

Perform the normal central setup ([03-central-setup.md](03-central-setup.md)) with these additions:

- **REQ-EXP-10** Shuffle the 13 new common Market cards into their matching Market decks.
- **REQ-EXP-11** Add the new Locations to the Starting or Advanced Location piles according to their position indicator.
- **REQ-EXP-12 Seed the Junk pile.** After creating the Market, move the top card of each of the four Market decks into the Junk pile.
  - This is done once per set in the game. With one base set plus this expansion, the Junk starts with 4 cards. With two combined base sets plus this expansion, it starts with 8.
- **REQ-EXP-13** Add the new common Ship tokens to the supply.
- **REQ-EXP-14 Reward pile.** Set aside every card whose position indicator says **REWARDS**. These form the central **Reward pile**. If another expansion already created a Reward pile, add these cards to it.
- **REQ-EXP-15** Player setup is unchanged.

## 3. New trait: Lower Decker

- **REQ-EXP-20** Lower Decker is a red-box special trait with gameplay meaning. The base rulebook lists it as unused; with this expansion it is active.
- **REQ-EXP-21** Every card with the Lower Decker trait has a **SUPPORT** operation.

## 4. SUPPORT operation

- **REQ-EXP-30** A SUPPORT operation starts with a trigger condition, like a REACTION.
- **REQ-EXP-31** When its trigger happens during the owner's **Action Step**, the player may play that Lower Decker card from **hand** into their Staging Area in response.
- **REQ-EXP-32** Resolve the SUPPORT operation's effect in full. Do **not** resolve any of the card's PLAY operations.
- **REQ-EXP-33** Afterwards the card stays in the Staging Area, unless an effect says otherwise, just like a played card.
- **REQ-EXP-34** SUPPORT can only be used from the hand. It cannot be used from any other zone.
- **REQ-EXP-35** A card put into the Staging Area by SUPPORT counts as put into play (see *Put into play* in [14-keywords.md](14-keywords.md)). This lets SUPPORT operations trigger each other in chains.
- **REQ-EXP-36** The engine treats SUPPORT as a trigger-driven option, like a Reaction. When a trigger happens, the owner gets a prompt listing every SUPPORT card in hand that matches. They may use any number of them, in any order, or none.
- **REQ-EXP-37** SUPPORT operations are shown on the card as a strip labelled SUPPORT. The card schema in [12-component-anatomy.md](12-component-anatomy.md) gains a `SUPPORT` operation type.

## 5. Crossover and the Reward pile

- **REQ-EXP-40** Cards meant for the Reward pile show **REWARDS** on their position indicator. They all have the **Crossover** trait. The base rulebook lists Crossover as unused; with this expansion it is active.
- **REQ-EXP-41** The Reward pile is a "virtual supply". Players can only gain from it through effects that explicitly name it.
- **REQ-EXP-42** Reward pile cards are never part of the Market. They cannot be scanned for, junked, gained with a Market effect, or otherwise affected by Market rules.
- **REQ-EXP-43** The Reward pile is never shuffled into the Market decks. The engine keeps it as a separate zone.
- **REQ-EXP-44** Currently only the Location *Krulmuth-B* uses the Reward pile. Its ACTIVATION looks at 2 **random** Crossover cards from the Reward pile. The engine must support drawing random cards from it.
- **REQ-EXP-45** Future expansions may add more Reward cards and new ways to get them. The Reward pile must be a general zone, not special-cased to *Krulmuth-B*.
- **REQ-EXP-46** Taking random cards from the Reward pile uses randomness, so it cannot be undone (see [20-undo.md](20-undo.md)).

## 6. Keyword clarifications

The expansion restates several keywords. Most match [14-keywords.md](14-keywords.md). These points are new or clearer:

- **REQ-EXP-50 Place resources.** Resources still on a card when it leaves play in any way (log, dismiss, recall, etc.), or when it is wiped from the Market, go back to the supply. The card's owner does **not** gain them.
- **REQ-EXP-51 Spend resources from a card.** When told to spend resources from a particular card, only that card's resources count. All other spending rules still apply: Glory can substitute, and resources return to the supply.
- **REQ-EXP-52 Treated as, for Skill icons.** Some cards let a player treat Skill icons of one colour as another colour. Examples:
  - "If you have a Weapon in play, all Military on your cards are treated as Any Skill instead."
  - "All of your Military are treated as Research instead. They cannot be used as Military any more; Any Skill icons can still be either."
- **REQ-EXP-53** When such an effect applies, the original colour is **gone** unless the card explicitly says otherwise. The engine must compute each card's effective Skill icons after applying all active "treated as" effects.

## 7. New Crew decks

| Captain | Faction | Complexity | Theme and play style |
|---|---|---|---|
| Pike | Starfleet | 5/10 | Many Person cards. Lacks the usual ways to climb Specialty tracks; instead, playing a skilled card advances a track. *Knowledge of a Terrible Fate* brings Time Travel. The *Time Crystal* gives early access to Developments. Strong at handling Incidents through medical expertise. |
| Riker | Starfleet | 6/10 | Strong Military. Needs extra effort to use Research via Utilize. Handles Incidents with *Deanna*'s advice. Features *Chateau Picard*, the Holodeck, two Boimlers, *Nepenthe*, the *U.S.S. Zheng He* and *Gluonic Distortion*. |
| Freeman | Starfleet | 7/10 | Built around Lower Decker cards and SUPPORT chains. Faces Encounters with many Ships. Allies matter for *Second Contact*. |

### Pike

- **REQ-EXP-PIK-01 Away Teams "4+".** Put 4 Away Teams on the Captain, and 1 more on *Starbase One*, Pike's starting Location.
- **REQ-EXP-PIK-02** If the Away Team on *Starbase One* is removed, it returns to Pike's Captain card as normal.

### Riker

- **REQ-EXP-RIK-01** Riker has a Status card, *Gluonic Distortion*, whose position indicator says **Development**.
- **REQ-EXP-RIK-02** During setup, put *Gluonic Distortion* in the Development pile. Do **not** put it into play like other Status cards.

### Freeman

- **REQ-EXP-FRE-01** The card *A Fleet of 30 California-Class Ships* has a SPECIAL operation: it counts as **two Ships** for securing a neutral Location. Its Ship token has two bases as a reminder.
- **REQ-EXP-FRE-02** The rule in REQ-EXP-FRE-01 applies whether a player or the Bot uses Freeman's deck.
- **REQ-EXP-FRE-03** The secured check in [05-resupply-and-control.md](05-resupply-and-control.md) and the Away Team placement check in [09-ships-locations-away-teams-beaming.md](09-ships-locations-away-teams-beaming.md) must use each token's **weight** (normally 1), not a plain count. The Away Team check compares Ship counts, so it must use the weight too.

## 8. Acceptance scenario: SUPPORT chain

From the expansion's example:

1. The player plays *K'ranch*: gain 1 Military, draw a card, log the drawn card to gain 2 Glory, then promote *K'ranch*.
2. Promoting a Person triggers *Bradward Boimler*'s SUPPORT: "After promoting a Person, duplicate the play operation of that card."
3. Boimler duplicates *K'ranch*'s PLAY: gain 1 Military, log another card to gain 2 Glory, then promote **Boimler**, because "this card" now means the duplicating card.
4. That exceeds the Duty Officer limit, so the player must dismiss one Duty Officer.
5. Promoting Boimler, a Lower Decker, triggers *D'Vana Tendi*'s SUPPORT: "After promoting a Lower Decker, gain 2 Research, Influence or Military, and you may promote this card to Duty Officer."
6. The player gains 2 Research and promotes *Tendi*. Her PASSIVE lets her stay on duty alongside Boimler.
