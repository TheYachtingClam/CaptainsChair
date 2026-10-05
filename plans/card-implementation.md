# Plan: implementing the remaining cards

Georgiou's deck and Cadet Training are done. This plan covers everything else, one step at a time. Each step ends with something you can test, and nothing in a later step is needed to test an earlier one.

## How every step works

1. **Before coding:** list the rulings the step needs. Rulings you've already given are recorded in the card specs. Any new question goes in `resources/scans/OPEN_QUESTIONS.md`, and I stop for your answer only when no sensible default exists.
2. **Build:** engine changes first, then the card modules. Every card is written from its spec, one file per card.
3. **Automated tests:**
   - one test per case in each spec's Tests section, in `server/tests/`;
   - the registry test (every operation implemented, `uses` only from the action list);
   - random-play games that force the step's cards into the decks, so every new operation runs at least once.
4. **Your test:** rebuild Docker, then try the step's cards in the browser using the developer panel from Step 1. Each step lists what to try.
5. **Finish:** update CLAUDE.md if the runtime changed, report, and wait for your go-ahead. You commit when you're happy.

## Status today

| Group | Cards | Operations with code |
|---|---|---|
| Market cards (Person, Cargo, Ship, Ally), all sets | 90 | 228 of 228 (Steps 2 to 7) |
| Locations, all sets | 23 | 0 of 56 |
| Common Incidents, Encounters, Directives | 17 | 2 of 34 |
| Reward pile (Second Contact) | 8 | 0 of 28 |
| Crew decks other than Georgiou | 194 | 41 of 551 |
| Crew board missions | 17 sides | none; no mission engine yet |

---

## Step 1: Test tools (done)

Nothing in the game changes. This step makes every later step testable by hand.

- **Developer panel**, shown only when `DEV_TOOLS=true` is set in `.env`. It can put any card into your hand, Staging Area or play area, add resources or actions, and move a Specialty track. Each use is recorded as a normal command, so undo and replay still work.
- **Scenario helper for tests:** `given(deck=..., hand=[...], duty=[...], tracks=...)` builds a game in a known position.
- **Coverage script:** `scripts/card_coverage.py` prints the status table above, so we can see progress after each step.

**You test:** turn on the panel, give yourself a Market card, and see it in your hand.

## Step 2: Market cards that need no new engine features (done)

Done as: every Market operation that needs no later feature, on all 90 cards. Each card module's docstring names the operations still waiting and the step they arrive in.

About 35 cards whose effects use only existing actions:

- the standard Ship operations, such as deploy, warp, and discard to beam;
- simple Allies: Bolians, Bynars, Denobulans, Kelpiens, Organians and Salt Vampires;
- simple Cargo: Plasma Manifold, Phasers PLAYs, Holosuite, Saurian Brandy, Kemocite and Universal Translator;
- simple Persons: Degra, Hoshi Sato's Find, Lursa, Tevrin Krit, Va'al Trask, Travis Mayweather's PLAY, Petra's Activation, Soji's PLAYs and Parmen's second PLAY.

Small engine additions:

- spending an Action token as a cost;
- free play from the Discard pile or a beamed card;
- the gainer of a Market card receives all resources on it, not only Glory.

**You test:** deploy and warp several Ships, beam cards to them, and play the Allies that log themselves.

## Step 3: New trigger events and resources on cards (done)

New events, each with REACTIONs that use them:

| Event | Cards that react |
|---|---|
| gaining a resource | Rom, Horta |
| logging a card | Kaelon II Science Ministry, Moopsy, Golden Statue of O'Brien |
| sending an Away Team | Phlox, Commander Tysess |
| taking or returning an Incident | Su'Kal |
| playing a named card | President Rillak |
| gaining a card onto your deck | Kazon Raider |
| putting a card with a trait into play | Petra Aberdeen, Soji Asha, Malik, Gift Box, Augmentation Plague, R.I.S. Talvath |

New actions: `PLACE_RESOURCES`, `MOVE_RESOURCES` and `TRIGGER_CONTROL`. Also the Talvath rule that keeps its resources when dismissed in your Control Step.

**You test:** use Horta's Reaction after gaining Dilithium. Place Dilithium on Kaelon and watch it move to the Market at Clean-up.

## Step 4: Attacks done properly (done)

- **The attack check:** an attack asks the defender whether to use a "when you would be attacked" Reaction, such as Riva or Phasers. If they use one, the negative effect is skipped (KW-ATK-03).
- **The "you were attacked" event,** for Admiral Jarok.
- **Pasalk's rule** that the opponent can't use Reactions on your turn.
- **Opponent choices:** the opponent discards, dismisses or logs, and makes the choice themselves (KW-FORCE).
- **New actions:** `STEAL` and `GIVE`, including Ambassador Gral replacing a returned Incident with a given one.
- **Cadet virtual opponent:** each attack resolves against it as "one of everything", for example steal 1 at most.
- **Existing cards:** Cmdr. Burnham and Kamran Gant move to the new attack check.

Cards: every Market card with ATTACK, about 20, plus Riva, Phasers and Jarok's Reaction.

**You test:** two browser windows, one per player. Attack from one and answer the forced choice in the other. With Riva on duty, ignore an attack.

## Step 5: Duty Officer slots, restrictions and modifiers (done)

- **Duty Officer slots** that only a certain trait may fill: Jarok for Starfleet, Rillak for Ambassador. Forced Singularity adds a slot only while you have 3 Military. Illyrians adds two slots from the Staging Area. A Duty Officer can't fill a slot it provides itself (KW-PROM-04).
- **Too many Duty Officers:** you're asked to dismiss one, including when Illyrians leaves at Clean-up.
- **Restrictions:** Jarok blocks playing or promoting Attack cards.
- **Modifiers:**
  - hand size: Ash Tyler, Talok and Thelev;
  - a temporary hand-size increase for Betazed Intelligence, which needs a new action;
  - Skill icons: Malik;
  - added traits: Protocol 12 gives your Doctors Augment.

**You test:** promote extra Starfleet officers with Jarok on duty. Try to play an Attack card and see it greyed out with the reason.

## Step 6: Duplicate, peek, and putting cards into the Staging Area (done)

- **`DUPLICATE`:** no extra action, requirements still apply, "this card" means the duplicating card, and a Duplicate can't copy a Duplicate (KW-DUP-01 to -05).
- **`PEEK`,** shown only to the player looking.
- **`PUT` into the Staging Area** without playing the card.
- **Taking control of the top Location,** for Landru.
- **A "before final scoring" moment,** for Su'Kal.

Cards: Tysess, Orb of Time, Holographic Drone Ship, Suliban, Vadic's Splinter Group, Sarina Douglas, Hoshi Sato's Activation, Landru and Su'Kal.

**You test:** use Orb of Time on a logged Denobulans. The Orb, not the Denobulans, should be logged (acceptance scenario AS-19).

## Step 7: SUPPORT from hand (Second Contact) (done)

- **SUPPORT offers:** when a trigger happens in your Action Step, matching SUPPORT cards in your hand are offered. A used card goes to the Staging Area and only its SUPPORT resolves. Chains can follow (REQ-EXP-30 to -37).
- **"When … would" SUPPORT:** Nova Fleet gains a card instead of junking it.

Cards: Jennifer Sh'reyan, Ma'ah, Nova Fleet and Drones of Cube 90182.

**Milestone:** every Market card is implemented.

**You test:** with Ma'ah in hand, put a Klingon into play and use the offered SUPPORT.

## Step 8: Missions (done)

The mission engine:

- completing a mission whose GOAL is met during the Action Step;
- the REWARD;
- mission tokens;
- dismissing beamed cards that helped (REQ-AS-30, -31, AS-15).

Goals and rewards for Georgiou's and Soval's board sides are included here. Each later Crew step adds its own.

**You test:** meet Georgiou's goal and complete the mission from the Action Step menu.

## Step 8b: Wildcard

The engine has no Wildcard rules yet (REQ-TR-05 to -07, AS-12). A Wildcard card counts as any single trait of its owner's choice: when finding or discarding by trait, and for "different species" counts. An opponent's attack cannot force it to count, and it is not any other trait at final scoring (REQ-FS-11). Vadic's Splinter Group already gains the Wildcard trait (Step 5); this step makes the trait mean something. Several Crew decks have Wildcard cards, so it comes before the Crew decks.

**You test:** discard a Wildcard card as an Engineer for Forced Singularity's Activation.

## Step 9: Common Incidents, Encounters and the two common Directives

17 cards. They mostly reuse Steps 2 to 4.

**You test:** take each Incident and play or return it. Take Encounters with Strange New Worlds.

## Step 10: Locations, the Reward pile and Stardates

- **Locations:** all 23 neutral Locations, with their CONTROL and ACTIVATION operations.
- **The Reward pile:** Krulmuth-B needs `TAKE_FROM_REWARD_PILE`, and the 8 Reward cards are added.
- **Stardates:** each Stardate card's effect moves from text matching to code, and is checked against its spec.

**You test:** secure and take control of Locations, then activate them. Play a Second Contact game and use Krulmuth-B.

## Steps 11 to 18: Crew decks, one per step

Each step covers the deck's cards, development costs, Passives, ENDGAME, deck-specific rules (REQ-CD-*), mission goals and rewards, and any Cadet Training differences. The order runs from simplest to most rule-changing:

11. Soval
12. Kirk
13. Archer: the set-aside Away Teams and putting cards on the Reserve
14. Pike (Second Contact)
15. Riker (Second Contact)
16. Freeman (Second Contact), including the K'ranch, Boimler and Tendi SUPPORT chain test
17. Rebner: hand size 3, Helmets, the Junk, and tracks fixed at ×0
18. Khan: marked traits, the double-sided Captain, his Incident rules, and his Cadet rules. Khan has two open questions to answer first.

**You test:** play a Cadet game with the new deck, then a two-player game against Georgiou.

## Step 19: Final sweep

- An engine test for every acceptance scenario AS-01 to AS-19 and the expansion and solo scenario lists that apply.
- The registry test made strict: every card in the content has a module.
- Remove the "not implemented yet" fallback.
- Go through the leftover open questions.

## Known rulings to settle when we reach them

These came out of the Market card specs. Each has a default I'd use if you have no preference.

- **Borg-only effects:** Borg Spatial Trajector's second PLAY, the Drones' second SUPPORT and the Borg Probe's assimilate branch need Borg content that doesn't exist. Default: they stay unusable.
- **Cloaking Device** makes a Ship "treated as Cloak" until end of turn. Nothing in these sets reads Cloak afterwards. Default: no effect.
- **Resources on a Market card** when someone gains it: settled by REQ-GN-06. The gainer takes every token on it.
- **Attacks against the Cadet virtual opponent.** Default: they work once against its "one of everything". For example, Ash Tyler dismisses its Duty Officer for 2 Glory, and stealing takes 1 from the supply.
