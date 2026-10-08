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
- That leaves about 48 new common cards and all 147 Crew cards.

Step 2 confirms these numbers by matching names once the Core Box cards are transcribed.

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

## Step 2: Specs

Transcribe every scan into a spec beside it, in the format of `resources/scans/CARD_SPEC.md`:

- 255 card specs, 12 board specs, 6 command-card specs;
- a new `same_as` field on each Core Box reprint, naming its *To Boldly Go* twin, checked by `scripts/build_content.py` (same name, traits, icons and text);
- deck sizes and suit counts checked against the scans in `tests/test_content_data.py`.

This is the largest step. I do it one folder at a time and list unclear text, icons I cannot read and rulings needed in `OPEN_QUESTIONS.md`.

**You test:** spot-check specs against the cards. Answer the open questions.

## Step 3: Requirements

- A new `requirements/23-core-box.md`: components, the six Crew decks' own rules (Burnham's Inert Dilithium and recrystallize above all), *Conspiracy*, promo set 1, and the box choice.
- Updates: REQ-CS-30 and -31 (box choice, combining), REQ-CS-20 to -23 (two promo sets), KW-RECRY-01, REQ-CTM-21, REQ-SOLO-59, -72 and -132, `02-components.md`, `15-crew-decks.md`, and gap 3 in `00-README.md`.
- Acceptance scenarios for combining boxes and for Burnham's Dilithium.

**You test:** read the new document.

## Step 4: Box choice and combined setup

- `new_game` takes the box choice. Core-only and combined setup follow REQ-CS-31: drop the `•` and `†` cards, shuffle the rest together, cut the Incidents to 6 before Crew Incidents are added, and seed the Junk.
- The API, the stored game and the new-game and new-campaign pages offer the choice and list only the Crews and Bots of the chosen box.
- Tests for each rule of REQ-CS-31, and that existing games replay unchanged.

**You test:** create a game with each box choice and check the Market, Locations and Crew list.

## Step 5: Common Market cards

- The 45 reprints: add each Core Box id to its existing module.
- The 9 old versions and the new Persons, Cargo, Ships and Allies, with any small engine additions they need.

**You test:** a Core-only game with Georgiou-style developer tools: put the new Market cards in hand and play them.

## Step 6: Locations, Encounters, Incidents and promo set 1

- The remaining common cards.
- The five promo cards. The server records the weekday with each command for *U.S.S. Enterprise-B* (decision 3).

**You test:** take control of new Locations; play the promo cards with promos on.

## Steps 7 to 12: Crew decks

One Crew per step: its cards, board missions, Cadet Training rulings and random-play games. Order, simplest first:

7. **Picard**
8. **Shran**
9. **Koloth**
10. **Sela**
11. **Sisko**
12. **Burnham**, with Inert Dilithium, recrystallize, her Clean-up rule and REQ-CTM-21

**You test:** a two-player game and a Cadet Training game with the step's Crew.

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
