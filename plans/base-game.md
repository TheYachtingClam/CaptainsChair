# Plan: adding the Core Box (base game)

The Core Box scans are in `resources/scans/base_game/`, with a first promo set in `resources/scans/promo1/`. This plan takes them from raw scans to playable content: media, specs, requirements, engine, cards, Bots and the campaign. Each step ends with something you can test.

The *To Boldly Go* rulebook already holds every rule (REQ-OV-12), so no Core Box rulebook is needed. What the Core Box adds is content, plus the few rules that live on its cards.

## What was scanned

| Folder | Holds | Count |
|---|---|---|
| `base_game/cards/ally`, `cargo`, `person`, `ship` | Market cards | 13 + 16 + 25 + 13 = 67 |
| `base_game/cards/location`, `encounter`, `incident` | Common cards | 20 + 8 + 6 = 34 |
| `base_game/cards/1DIR01`, `1DIR02` | *Conspiracy* (solo challenge) and *Reinforce* (solo campaign) | 2 |
| `base_game/cards/captains/<Crew>` | Burnham 26, Sisko 25, Picard 24, Shran 24, Koloth 24, Sela 24 | 147 |
| `base_game/boards` | Crew boards, basic and advanced | 12 sides |
| `base_game/command` | Automated Command cards: traits, two suits sides, upgrades | 24 sides |
| `base_game/ships` | Ship tokens, front and back | 32 tokens |
| `promo1/cards`, `promo1/ships` | *U.S.S. Enterprise-B*, *Sehlat*, *Wesley Crusher*, *Flight Training Accident*, *Whale Probe Incursion*; one Ship token | 5 cards, 1 token |
| `promo2/ships` | The *U.S.S. Cabot* token, moved here from `to_boldly_go/ships` | 1 token |

That is 250 Core Box cards and 5 promo cards.

Not scanned, and how the plan handles it:

- **Stardate cards.** Every box choice uses the *To Boldly Go* Stardate cards (decision 2).
- **Card back, Away Team tokens.** The existing images are reused.
- **Rulebook.** Not needed.

## How it overlaps with *To Boldly Go*

*To Boldly Go* reprints 45 Core Box cards (marked `•`, already `box_marker: duplicate` in the specs) and replaces 9 (marked `†`, `box_marker: replacement`).

- The 45 reprints need no new code. The Core Box id is added to the existing card module's id list, as identical copies in Crew decks already are.
- The 9 replaced cards are old versions. They are played only in a Core-only game, and each needs its own spec and code.
- That leaves 48 new common cards. Of the 147 Crew cards, 33 are copies of cards that already have code, so 114 are new.

Step 2 confirmed these numbers by matching names.

## New rules seen on the cards

From a sample of each Crew's first six cards, the Directives, one board, one Bot and the promo set. Step 2 produces the full list.

- **Burnham.** *Inert Dilithium* (Status): Dilithium gained anywhere but from the Market goes onto this card and cannot be spent; **recrystallize** moves it to your supply (KW-RECRY-01); Glory cannot be spent as Dilithium; hand size +1. Her Captain replaces the Clean-up Glory with 2 Dilithium on a Market card (REQ-CTM-21, REQ-SOLO-59). *U.S.S. Discovery-A*: "Your Dilithium cannot be stolen." *Adira Tal*: "When you would gain a card, scan 2 of the same suit instead." Her board's first mission rewards "the top Discovery" (decision 5).
- **Picard.** *Phasing Cloak*: ignore opponent Ships when sending Away Teams to neutral Locations, as a standing rule. Development cost "find a Person and log it".
- **Koloth.** *Prototype Cloak*: a Ship gains Cloak for the rest of the turn. *Boreth*: draw the bottom card of your deck. Development costs "have 10+ Glory" and "free if *I.K.S. Devisor* is in play".
- **Sela.** "After attacking your opponent" on her Captain. Cards named in text: *Infiltrate*, *Conquer*, *Scimitar*.
- **Sisko.** *Orb of the Emissary*: an Encounter in his Development pile that "cannot be played". *Self-Replicating Mines*: a Reaction to the opponent gaining Influence or Military, and a Passive that ignores an attack and logs itself. *Deep Space 9*: a Ship that cannot be warped, and can recall a card beamed to it.
- **Shran.** Nothing new in the sample.
- **Conspiracy** (1DIR01): cannot be beamed or discarded except by its own PLAY; destroyed before scoring if the Bot owns it or it is logged; −4 VP; a SURPRISE where you choose between two penalties. REQ-SOLO-132 already allows it as a second Ticking Clock.
- **Promo set 1.** *Wesley Crusher*: use the Activations and Reactions of any Person in your Staging Area. *U.S.S. Enterprise-B*: "If it is a Tuesday" (decision 3). Both Incidents replace a random Incident at setup, as *Subspace Rhapsody* does (REQ-CS-22).
- **Burnham Bot.** Its special rule is already in REQ-SOLO-59 and REQ-SOLO-72. Its rows gain "the card in the Market with the most Dilithium, then most Glory".

Most of this fits the existing actions and registries. Recrystallize and Inert Dilithium are the one real engine addition; the rest are new registry entries or small options on existing actions. Any new action follows "Changing the action list" in CLAUDE.md.

## Decisions

Answered on 2026-10-08:

1. **Box choice.** A new game picks a box: *Core Box*, *To Boldly Go* or *Both combined*. Crew decks are limited to the chosen box (REQ-CS-30); *Both* applies REQ-CS-31.
2. **Stardate cards.** Every box choice uses the *To Boldly Go* Stardate cards.
3. **"If it is a Tuesday"** (*U.S.S. Enterprise-B*). The real day when the card is played. Card code may not read the clock, so the server records the weekday with each command and the engine reads it from there; replay and undo then give the same answer.
4. **Scope.** Everything scanned, including the six Bots and their Five-Year Mission upgrades.

Defaults I am using unless you say otherwise:

5. **"Discovery" on Burnham's board** means Encounter (the pill carries the Encounter icon).
6. **Promo cards.** The one "include promo cards" option covers both promo sets.
7. **File names.** The new scans are renamed to the existing conventions (done in Step 1).
8. **Second Contact** is allowed with any box choice, as its rules say it needs "the Core Box or *To Boldly Go*".

## How every step works

As in [card-implementation.md](card-implementation.md): rulings first, engine changes before card modules, one test per case in each spec's Tests section, then your test in the browser, then CLAUDE.md and a report. New questions go in `resources/scans/OPEN_QUESTIONS.md`; I stop only when no sensible default exists.

A card enters `server/content/` in the step that writes its code, so the strict registry test stays green throughout.

---

## Step 1: Media (done)

- Rename the scans to the conventions.
- Write the Ship token mappings; move the *Cabot* lines from the *To Boldly Go* mapping to `promo2/ships`.
- Run `scripts/process_scans.py`. Check every id is unique and every image opens.
- Update `resources/scans/README.md` and CLAUDE.md for the `base_game` and `promo1` sets.

**What was done:** boards are `cb-<crew>-<side>.jpg`, command sides `<crew>-traits`, `-no-duty-officer`, `-with-duty-officer` and `-five-year-mission-upgrades`, the Ship card folder is `cards/ships/`, Crew folders are lower case, and the promo card files are upper case. `mapping.csv` files in `base_game/ships`, `promo1/ships` and `promo2/ships` name the 34 tokens by card id. 357 new images are in `server/content/images/base_game/` and `promo1/`, and the *Cabot* token images moved to `promo2/`. No card data or code changed, so nothing shows in a game yet.

**You test:** open a few of the new images at `/api/content/images/{id}`: `1BUR01`, `cb-sisko-advanced`, `koloth-traits`, `ship-1pic02`.

## Step 2: Specs (done)

Transcribe every scan into a spec beside it, in the format of `resources/scans/CARD_SPEC.md`.

**What was done:**

- **255 card specs**: 250 Core Box and 5 promo. `server/content/cards/base_game.yaml` and `promo1.yaml` are built from them.
- **12 board specs** with tracks and 18 missions, and **6 command-card specs** with 126 rows and 24 upgrade bonuses.
- **Reprints.** A new `same_as` field names an identical card; `scripts/build_content.py` checks that the two print the same data. 45 common Core Box cards point at their *To Boldly Go* reprint, and 33 Crew cards point at a card that already has code (*Utilize*, *Recruit*, *Analyze*, *Set a Course* and so on). A new `replaced_by` field marks the 9 old versions.
- **What is new to write:** 58 common cards (the 48 new ones, the 9 old versions and *Conspiracy*), 114 Crew cards, 5 promo cards, 18 missions, 126 Bot rows and 24 bonuses.
- **Waiting, on purpose.** The Core Box Crews, cards and Bots are in the content but not offered anywhere: `setup.BOT_UNAVAILABLE` lists the six Bots, games still use only *To Boldly Go* and its expansions, and the registry tests skip `WAITING_SETS` and `WAITING_CREWS` until each step writes the code.
- **Questions and engine needs** are in `resources/scans/OPEN_QUESTIONS.md`, under "Core Box and promo set 1" and "Gaps in the CLAUDE.md action list".

How the specs were made: I read every card, board and command card from the scans and wrote the specs from that reading. The reprints' specs are copies of the *To Boldly Go* specs, compared on screen but not word for word.

**You test:** spot-check specs against the cards, above all Burnham's deck and the two Skill-icon readings noted in the open questions. Answer the open questions.

## Step 3: Requirements (done)

- A new `requirements/23-core-box.md`, and updates to the documents that pointed at missing Core Box content.

**What was done:**

- **`23-core-box.md`** (REQ-CORE-01 to -63): components, choosing a box, combining boxes, Burnham's Inert Dilithium, recrystallize and Clean-up rule, the other Crews' rules, *Sha Ka Ree*, the promo cards, the six Bots and *Conspiracy*, and eight acceptance scenarios (CORE-AS-1 to -8).
- **Combining boxes** is now exact: 105 Market cards, 29 Locations, 13 Encounters, Incidents cut from 8 to 6, Junk seeded with 4.
- **Updated:** REQ-CS-20, -30 and -31, KW-RECRY-01 to -03, REQ-CTM-21, REQ-SOLO-132 and -133, REQ-SRV-18, a new REQ-SRV-52 (the server stores the weekday with each command), the document map and gap 3 in `00-README.md`, and pointers in `02-components.md` and `15-crew-decks.md`.
- Three requirements are marked "ruling, to confirm": REQ-CORE-32 (Burnham's starting Dilithium is in her supply), REQ-CORE-43 ("Discovery" is Encounter), and the defaults they share with `OPEN_QUESTIONS.md`.

No code changed. The acceptance scenarios get their tests in the step that builds each feature.

**You test:** read `requirements/23-core-box.md`, above all §2 (choosing a box) and §4.1 (Burnham).

## Step 4: Box choice and combined setup (done)

- `new_game` takes the box choice, and the API, the stored game and the pages offer it.

**What was done:**

- **Engine.** `new_game(..., box=)` with `setup.BOXES` (`core`, `to_boldly_go`, `both`); `state.box` records it. `setup.common_cards` picks the common cards: with both boxes it leaves out each Core Box card that *To Boldly Go* reprints or replaces. Combined setup cuts the Incidents to 6 and seeds the Junk (REQ-CORE-20 to -24). The default box is *To Boldly Go*, and such a game is set up exactly as before.
- **Server.** `Game.box` and `Campaign.box` columns (older rows are *To Boldly Go*), `box` on game and campaign creation, Crew and Bot checks against the box, and `GET /api/content/boxes`. The six Core Box Crews are in `content/decks.json`, without a complexity, which their components do not print.
- **Client.** A Box choice on the new-game and new-campaign pages; the Crew and Bot lists follow it; the lobby and game table show the box.
- **Tests.** `tests/test_core_box.py` (CORE-AS-1 and -2, REQ-CORE-03, -11, -20 to -27) and two API tests in `tests/test_games.py` (CORE-AS-3).
- **Not yet:** Core Box cards, missions and Bots have no code, so in a Core Box game most cards log "Card effect not implemented yet", and no Core Box Bot can be chosen. Random two-player and Cadet games with every Core Box Crew run to the end without errors.
- **Promo set 1** is not added by the promo option yet. It joins in Step 6 with its code, behind a stored flag so that games already created with promos replay unchanged.

**You test:** create a game with each box choice and check the Market, Locations and Crew list. In a Core Box game the cards show but mostly do nothing yet.

## Step 5: Common Market cards (done)

- The reprints, the old versions and the new Persons, Cargo, Ships and Allies.

**What was done:**

- **Reprints and copies.** `cards.link_copies()` gives every card whose spec says `same_as` the operations and registry entries of its twin. All 45 reprints and the 33 Crew copies of existing cards are covered without a module of their own.
- **40 Market cards written**, one module each in `server/engine/cards/base_game/`: 5 Allies, 10 Cargo, 17 Persons and 8 Ships. That is the 32 new Market cards and the 8 old versions.
- **Old versions.** *Lirpa*, *Holographic Drone Ship* and *U.S.S. Enterprise-C* play differently from their *To Boldly Go* versions and have their own code. *Phlox* and *Kazon Raider* print the same text and are registered with the newer card. *Orb of Time*, *Phasers* and *Borg Spatial Trajector* play the same but are worded differently, so they have their own modules; an existing test requires shared code to have identical text. *Solum*, a Location, was done here too.
- **Engine.** One addition: `peek_and_reorder(n, deck=)` now also works on the Location and Encounter decks (*Unstable Wormhole*).
- **Tests.** `tests/test_core_market.py`: 40 tests, one or more per card with logic. The existing "every operation runs" test now covers every Core Box Market operation. 40 random two-player games with Core Box and mixed Crews ran to the end.
- **Rulings made** are in `resources/scans/OPEN_QUESTIONS.md` under "Core Box and promo set 1".

**You test:** a Core Box game with the developer panel: put the new Market cards in hand and play them.

## Step 6: Locations, Encounters, Incidents and promo set 1 (done)

- The remaining common cards and the five promo cards.

**What was done:**

- **9 Locations and 5 Encounters** in `server/engine/cards/base_game/`, and **5 promo cards** in `server/engine/cards/promo1/`. Every common Core Box card now has code except *Conspiracy*, which waits for the Bots (Step 13). The common Incidents needed nothing: all six are reprints or copies.
- **The weekday** (REQ-SRV-52). The server stores the weekday with each command and sets `state.weekday` before applying or replaying it; *U.S.S. Enterprise-B* reads `ctx.weekday()`.
- **Promo sets.** New games with promos get both sets, stored in `Game.promo_sets`. Games created earlier keep promo set 2 only, and one such setup was compared field by field with the setup before this change.
- **Promo Incidents** each replace a different random Incident (`REPLACES_AN_INCIDENT`). With both boxes, the cut to 6 now happens before the promos replace any; before, a promo Incident could be cut.
- **Sha Ka Ree** goes among your controlled Locations when played, which counts as taking control.
- **Wesley Crusher** is a Person who can be promoted, and lets you use the Activations and Reactions of Persons in your Staging Area (`STAGING_PEOPLE_ACTIVE`).
- **The promo SURPRISE operations** are written; `resolve_bot_top` lets *Flight Training Accident* resolve the Bot's next card.
- **Tests.** `tests/test_core_common.py` (24 tests) and two API tests. The existing generic tests now run every operation of these cards as well.

**You test:** take control of the new Locations; with promos on, play the promo cards. On a Tuesday, *U.S.S. Enterprise-B* offers an Away Team.

## Steps 7 to 12: Crew decks

One Crew per step: its cards, board missions, Cadet Training rulings and random-play games. Order, simplest first:

7. **Picard** (done)
8. **Shran** (done)
9. **Koloth** (done)
10. **Sela** (done)
11. **Sisko** (done)
12. **Burnham**, with Inert Dilithium, recrystallize, her Clean-up rule and REQ-CTM-21

**You test:** a two-player game and a Cadet Training game with the step's Crew.

### Step 7: Picard (done)

- **17 cards** of his own in `server/engine/cards/base_game/`; his other 7 are copies that already worked. The *U.S.S. Enterprise-D* prints the same operations as the *U.S.S. Shenzhou* and is registered with it (as is Shran's *Kumari*).
- **3 missions** in `missions_picard.py`: *Peace Negotiations*, *Arbiter of Succession*, *Seek Out New Life*.
- **8 development costs**, including "take an Incident" (*Tamarians*) and "find a Person and log it" (*Phasing Cloak*).
- **Engine:** one new registry, `IGNORE_OPPONENT_SHIPS`, for *Phasing Cloak*. *Deanna Troi* uses the existing granted-PLAY registry.
- **Tests:** `tests/test_picard.py`, 61 tests: every operation, each mission, 6 random two-player games against other Crews and a Cadet Training game.
- Picard can be chosen in Core Box and combined games. His Bot and campaign bonuses come in Steps 13 and 14.

### Step 8: Shran (done)

- **19 cards** of his own; *Kumari* shares the *Shenzhou*'s code and 4 are copies. *Confiscate* and *Imperial Pride* are written here and shared with Koloth's and Sela's copies.
- **3 missions** in `missions_shran.py`: *Securing Andoria's Borders*, *Founding the Federation*, *Andorian Mining Consortium*.
- **Engine:** three small options on existing actions: `discard_from_deck(player=opponent)` (*Tarah*), `return_incident(player=opponent)` (*Ambassador Thoris*), and an `EffectCost` may record what it used in `actions.paid` (*Imperial Pride*).
- **Tests:** `tests/test_shran.py`, 60 tests, with 6 random games and a Cadet Training game.

### Step 9: Koloth (done)

- **19 cards** of his own; 5 are copies. *I.K.S. Klothos* shares the first four operations of *I.K.S. Gr'oth*. *Conquer* is written here and shared with Sela's copy.
- **3 missions** in `missions_koloth.py`: *Expanding the Empire*, *Romulan Weapons Trade Agreement*, *Sabotage* (an ATTACK reward).
- **Development costs with conditions:** "have 10+ [Glory]" (*Boreth*, *Kor*), "have 8+" (*Kang*), and "free if the *I.K.S. Devisor* is in play" (*Sword of Kahless*), all with the existing `Condition` and `SpendUnless` costs.
- **Engine:** one option, `draw(bottom=True)`, for *Boreth*.
- **Tests:** `tests/test_koloth.py`, 63 tests, with 6 random games and a Cadet Training game.
- **Added after Step 9 (decision, 2026-10-09):** the turn-long Cloak is tracked. A new action, `TREAT_AS`, gives a card a trait until the end of the turn (KW-TREAT-05); *Cloaking Device* and *Prototype Cloak* use it.

### Step 10: Sela (done)

- **17 cards** of her own in new modules; 5 are copies. *Forced Singularity* and *Infiltrate* print the operations of cards that already existed (2CAR06, 2KHA09) and are registered with them; her three plain Warbirds share one module, and *I.R.W. Valdore* shares their PLAY.
- **3 missions** in `missions_sela.py`: *Romulan Might*, *The Reunification Plot*, *The Duras Plot*, which reads the turn-long Cloak.
- **Engine:** in Cadet Training an attack now raises the `attacked` event for the attacker's own effects, so Sela is paid there too. Logging an opponent's Location (*Scimitar*) needed nothing new.
- **Tests:** `tests/test_sela.py`, 67 tests, with 6 random games and a Cadet Training game.

### Step 11: Sisko (done)

- **19 cards** of his own in new modules; 6 are copies. *U.S.S. Rio Grande* shares a PLAY with Picard's *Type 7 Shuttlecraft*, and *Deep Space 9* shares the *Shenzhou*'s promote. *Orb of the Emissary* has a development cost and no operations.
- **3 missions** in `missions_sisko.py`: *A Call to Arms*, *Bajor's Application to the Federation*, *Contacting the Dominion*.
- **Engine:** `enlist_development(discount=n)` and `discount="both"`; the `spend` event says how much Latinum and Dilithium an operation's cost asked for (*Quark*); a PASSIVE "when you would be attacked" runs before any Reaction is offered and is not optional (*Self-Replicating Mines*); playing a Crew Location from hand now raises `take_control`, as KW-TC-02 says, so *Benjamin Sisko*, *Wajahut*, *Chancellor Gowron*, *Proconsul Neral* and *Ambassador Kamarag* react to it.
- **Tests:** `tests/test_sisko.py`, 71 tests, with 6 random games and a Cadet Training game.

## Step 13: The six Bots

- Automated Command rows for each Crew, one function per row.
- The Burnham Bot's special rule (REQ-SOLO-59, -72).
- *Conspiracy* and its SURPRISE (REQ-SOLO-132), and the SURPRISE operations on the Core Box and promo Incidents.

**You test:** a solo game against each new Bot; one with *Conspiracy* as the Ticking Clock.

## Step 14: Five-Year Mission upgrades

- Option A restrictions and option B bonuses for the six Crews.

**You test:** a campaign assignment against a Core Box Bot, then pick each kind of upgrade.

## Step 15: Final sweep

- Random games for every Crew and Bot with each box choice, in the solo and campaign sweeps.
- `scripts/card_coverage.py` shows every group done.
- CLAUDE.md, the requirements index and `OPEN_QUESTIONS.md` are up to date.
