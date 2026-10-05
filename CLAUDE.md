# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

An online version of the board game *Star Trek: Captain's Chair*.

- `requirements/` holds the requirements. Start at `requirements/00-README.md`. They are the source of truth. If code and requirements disagree, stop and flag it rather than guessing.
- `resources/` holds source material that is **never** copied into the Docker image:
  - `resources/scans/<set>/`: everything for one product, by kind: `cards/`, `boards/`, `command/`, and the rulebook scans in `manual/` and `solo/`. See `resources/scans/README.md`.
- `server/content/images/` holds the processed images the server ships and serves, at `/api/content/images/{id}`. Regenerate them with `scripts/process_scans.py`; never edit them by hand.
- `server/` is the Python API server and rules engine (FastAPI, pytest). `client/` is the React and TypeScript web client. See `requirements/19-technical-architecture.md`.
- Rule precedence: card text beats Keywords in Detail (`requirements/14-keywords.md`), which beats the general rules.

## Commands

```bash
scripts/start.sh --test     # server tests (run after every server change)
scripts/start.sh --dev      # API with reload on :8000, client on :5173
cd client && npm run build  # type-check and build the client
scripts/process_scans.py    # raw scans -> server/content/images/<same folders>/<id>.webp
scripts/build_content.py    # card and board specs -> server/content/cards/*.yaml and boards.yaml
scripts/card_coverage.py    # how many card operations have code; --missing lists the rest
```

## Engine

`server/engine/` is the rules engine. It has no web or database code.

| Module | Holds |
|---|---|
| `state.py` | `GameState`, players, zones, card instances, decisions, events. One serialisable object |
| `setup.py` | Central and player setup (`new_game`) |
| `game.py` | The turn loop (`advance`), `choose` for player answers, and shared rules: draw and deck cycling, Glory and Stardates, Control, the Burn, Market and Neutral Zone wipes |
| `scoring.py` | Final scoring and the Burn count |
| `views.py` | Per-player views that hide secrets |
| `content.py` | Card and board data loaded from `server/content/` |
| `cards/` | Card code, one module per card |

Rules for engine code:

- All player input goes through a `Decision`: the engine stops, lists the options, and continues when `choose` gets an answer. Never block or prompt any other way.
- All randomness goes through `state.shuffle` or `state.rng()`. They derive from the seed and a counter, so replay and undo give the same result.
- Mark every event that reveals hidden information, uses randomness or ends a turn with `irreversible=True`. Options are flagged for the can't-be-undone warning by trying each one on a copy of the state.
- The server stores the seed and the list of commands, and rebuilds a game by replaying them (`server/app/play.py`). Undo marks the last command undone and replays.
- Developer commands (`engine/dev.py`) put any card into a zone or change resources and tracks, for testing by hand. The server accepts them only when `DEV_TOOLS=true`. They are stored and replayed like moves. Card tests build positions the same way with `given(...)` in `server/tests/scenario.py`.

## Solo mode (the Bot)

`server/engine/bot/` runs the Bot in solo mode ([plans/solo-mode.md](plans/solo-mode.md), requirements/22-solo-mode.md):

- The Bot is the second entry in `state.players`, with `player.bot` set (Crew, difficulty, SUITS side, Ticking Clock, facedown cards). Its cards use the normal zones: `draw` is the Bot deck, `reserve` the Supplement deck, `discard` the Bot Discard pile, `staging` its Staging Area, and `duty`, `locations` and `fleet` its Control Area. It never has a hand.
- Its turn is the `bot` step of the turn loop. The engine runs it without stored commands, so replay still needs only the seed and the human's commands. A question put to the Bot is answered at once by `bot.answer` (REQ-SOLO-112). The Bot never gets Reactions or "when … would" offers, and has exactly one Duty Officer slot.
- `bot.value`, `most_valuable` and `least_valuable` are the one value function for every Bot choice (REQ-SOLO-43).
- Your cards against the Bot need no special code; the ordinary actions handle it (requirements/22-solo-mode.md §8, §12): a draw for the Bot discards the top of its deck; a forced discard from its (empty) hand asks you whether it succeeded, and lets you move its top discard onto its deck (`bot_hand_attack`, which card code also calls directly, e.g. Harry Mudd); steals come from the supply; a recalled Bot card is discarded; Incidents given to it go on top of its deck; losing its Duty Officer flips its SUITS card back. `bot.answer` declines Incident returns and gives up its most recently deployed Ship. Effects that let it choose from its hand or Discard pile check `opp.bot` and use only its cards in play.
- SURPRISE operations are card code (an `@operation` of kind SURPRISE) run with the Bot as `ctx.me`; "you" is `ctx.opponent`.
- Automated Command data is built by `scripts/build_content.py` from `resources/scans/<set>/command/*.md` into `server/content/command.yaml` (`content().command`).
- Each card the Bot resolves runs as an operation of mode `bot` (`bot.resolve_op`), so the human's questions inside it pause and replay like card operations. Matching (`bot.resolve`): SURPRISE first, then TRAITS rows top to bottom (a Wildcard matches each in turn), then the suit row on the SUITS side face up; "continue resolution" moves to the next match; a Location left in the Staging Area goes to the Control Area.
- Rows are code, one function per row, in `server/engine/bot/<crew>.py`, registered with `@row(crew, side, number, uses=[...])` where side is `traits`, `no_duty_officer` or `with_duty_officer` and `number` is the row's number in the spec. The `uses` list must equal the spec's Actions column (a test checks). Crew special rules that are data go in `LOG_TOP_DISCARDS` and `VALUE_BONUS`.
- A row receives `BotActions` (`engine/bot/actions.py`), the Bot's versions of the actions: `gain_card("A > B / C", take=, from_junk=, including_junk=)` picks the most valuable match (gain to the Bot Discard pile, take onto the Bot deck); `log_top`, `discard_top`, `resolve_top`, `resolve_supplement_top`; `promote` and `dismiss_duty_officer`/`log_duty_officer` flip the SUITS card; `deploy`, `explore`, `engage`, `send_away_team(prefer=, target=)`; `gain_lowest`/`gain_highest`; `continue_resolution`. The human's bold parts: `attack()` (their "when attacked" Reactions apply), `human_removes_away_team`, `human_may_return_incident`.

## Card specs

Every card scan in `resources/scans/<set>/cards/` has a spec file beside it with the same name and a `.md` extension. Crew board specs are in `resources/scans/<set>/boards/` and command-card specs in `resources/scans/<set>/command/`. The format is in `resources/scans/CARD_SPEC.md`.

- Write a card's code from its spec, not from the scan. The spec lists each operation's cost, requirements, effect steps, choices, and the exact `uses=` actions.
- Each spec's Tests section lists the cases its test module must cover.
- If code and spec disagree, fix the spec first, then the code.
- After editing any card or board spec, run `scripts/build_content.py`. Never edit `server/content/cards/` or `server/content/boards.yaml` by hand. The engine loads them through `engine/content.py`.
- `resources/scans/OPEN_QUESTIONS.md` lists rulings still to be decided and actions missing from the list below. Do not implement a card with an open question until it is resolved.

## Card effects are code

This section is mandatory for every card. It also applies to everything else with an effect:

- Crew board missions (goal and reward);
- Stardate card effects;
- the Bot's Automated Command rows;
- solo campaign upgrade bonuses.

### Rules

1. **Every card operation is one Python function.** Each operation printed on a card becomes its own function: PLAY, ACTIVATION, PASSIVE, REACTION, SUPPORT, CONTROL, RESUPPLY, CLEAN-UP, ENDGAME, SPECIAL, SURPRISE and development costs. Nothing is interpreted from rules text at runtime. Printed text is stored only for display.
2. **Each operation declares the actions it may take.** The `uses=` list on the `@operation` decorator names every action the operation can call.
3. **The engine passes in only those actions.** The operation receives an `actions` object holding exactly the actions in its `uses` list. Calling any other action raises `UndeclaredActionError`. An operation cannot do anything it did not declare.
4. **State changes only through actions.** Card code never edits game state directly. It never uses `random`, the clock, files, the network or module-level mutable state. The engine owns randomness so games replay exactly and undo works (`requirements/20-undo.md`).
5. **Card code never decides for a player.** Every choice, including every "may", goes through `actions.choose(...)` or `actions.may(...)`. The engine asks the right player, or applies the Bot rules in solo games. These two are always available and need no declaration. A required `pick_card` with exactly one candidate picks it without asking; optional picks always ask.
6. **Every action is a generator. Call it with `yield from`.** Any action can pause the operation for a player decision, for example a Reaction, a Wildcard choice or enlisting a Development during a reshuffle. `yield from` lets the engine suspend and resume the operation.
7. **Traits go through `has_trait` (or `ctx.has`).** It counts "treated as" traits and Wildcard: a Wildcard card counts as any single trait for its owner's own checks, never for the opponent's, and never at final scoring (REQ-TR-05, REQ-FS-11). The engine knows whose check it is from the operation running. Use `printed_trait` only when a rule says printed traits, and `distinct_traits` for "each different one of" counts.
8. **Reading is free.** Read the game through `ctx`, the read-only query object: traits in play, token counts, tracks, zones, `ctx.this_card`, `ctx.me`, `ctx.opponent`. Queries need no declaration and never change state.
9. **Costs and requirements are declarative.** Put costs in `cost=` as cost objects from `engine.ops`: `Spend` (resources and Action tokens), `DiscardFromHand`, `TakeIncidentCost`, `PutOnDeck`, `LogFromHand` (from hand, Discard pile and/or play), `DismissFromPlay` (beamed cards too), `DismissDutyOfficer`, `RemoveOwnAwayTeam` (`here=True` for this Location), `SpendUnless(Spend(...), free_if)` ("X, or free if ..."), `SpendVariable(lambda ctx: {...})` ("[Dilithium] x every 2 [Military]"), `EffectCost(test, effect, uses)` (a cost that is an effect, e.g. "find 3 Person and beam them to the same Ship"), `ExhaustCaptain` and `Condition` (a precondition that pays nothing, e.g. "have 1+ Vulcan logged"). Put "Requires ..." conditions in `requires=lambda ctx: ...`. The action icon is not a cost: the engine reads it from the printed card data and spends the action itself. The engine checks costs and requirements to decide whether the operation is legal, and pays the costs before running the body. Cards used to pay are in `actions.paid`, for "discard a card to ... matching the discarded card". The body contains effects only. An operation whose cost cannot be paid can never start (REQ-AS-04, KW-REQ-02).
10. **Attacks are checked.** Declare `A.ATTACK` and write `if (yield from actions.attack()):` before the parts that target the opponent; resolve them only when it returns True. The defender may use a "when you would be attacked" Reaction first (Riva, Phasers), which makes it return False (KW-ATK-03). Pass `removes_away_teams=True` when the negative effect removes Away Teams. Call it once per operation; later calls return the same answer, and the engine makes the check after any ATTACK operation that never called it. Choices the opponent makes (KW-FORCE) go through `pick_card(..., seat=opponent.seat)`, `discard(..., player=opponent)` or `may(..., seat=...)`, and need `A.FORCE`. `steal` and `give_incident` handle the Cadet virtual opponent themselves.
11. **Handle the Cadet Training virtual opponent.** In Cadet mode `ctx.opponent` is None and `ctx.virtual_opponent` is True. The virtual opponent has one of everything except Ship tokens at neutral Locations, so effects against it apply at most once (REQ-CTM-12). For "the opponent takes an Incident", call `actions.take_incident(opponent=True)`; in Cadet mode it gives you 1 Glory instead (REQ-CTM-13).
12. **"This card" means `ctx.this_card`.** Never hard-code a card identity for "this card". Duplicate effects rely on it pointing at the duplicating card (KW-DUP-04).
13. **One file per card.** Never put card-specific logic in the engine core, and never add an action named after a card.

### Operation kinds

| Kind | Function shape | Notes |
|---|---|---|
| PLAY, ACTIVATION, CONTROL, RESUPPLY, CLEAN-UP, SPECIAL, SURPRISE, SUPPORT | `@operation(ids, index, ...)` generator `fn(ctx, actions)` | ACTIVATION and REACTION exhaust automatically. Do not declare exhaust as a cost |
| REACTION, triggered PASSIVE, SUPPORT | The same, plus `trigger=lambda ctx, event: bool` | Events are dicts with `kind`, `seat` (whose event it is) and `uid` (the card, which `ctx.event_card` finds). Kinds: `put_into_play` (`played` when by playing it, `beamed` when by beaming it), `deploy`, `warp` (`location`), `gain` (`to`: hand, top or discard), `gain_resource` (`resource`, `amount`; not on stealing), `gain_specialty`, `log` (`by`: who logged it), `send_away_team` (`location`, `controlled`, `neutral`), `take_incident` (also when given one), `return_incident`, `exhaust`, `attacked` (`attacker`), `take_control`, `spend` (`dilithium`, `latinum`, `glory` actually paid), `discard` (`step`), `promote`, `junk` (`source`), `draw` (`count`, `source`: the card whose operation drew; uid is None), `support_resolved` (after a SUPPORT finishes) and `mission_completed`. A SPECIAL with a `trigger` also fires from wherever its own card is, when the event is about that card ("When you log this card"), and from the Staging Area for any event ("While this card is in your Staging Area, after ..."; it asks its own "may"). "When … would" Reactions and SUPPORTs see `would_attack` (`removes_away_teams`), `would_return_incident`, `would_junk`, `would_gain` (True adds the Junk as a source) and `would_gain_market` (`suits`; True replaces the gain); their function returns True when it replaced or cancelled the event. Triggered PASSIVEs are mandatory. REACTION and SUPPORT are offered to the player. REACTION and PASSIVE work only from table positions; SUPPORT only from hand, during the owner's Action Step: the engine moves the card to the Staging Area (put into play) and resolves only the SUPPORT (REQ-EXP-30 to -37) |
| Continuous PASSIVE | A registry decorator: `@hand_size_modifier`, `@skill_icons`, `DUTY_LIMIT[id] = n`, `SCANS_INCLUDE_JUNK.add(id)`, `@state_check`, `@dismiss_rewards` (resources gained when the card is dismissed), `@duty_slots` (extra Duty Officer slots, optionally for one trait), `@restriction` ("you cannot play or promote"), `@trait_modifier` ("treated as"), `ALSO_SUIT[id] = suit` ("considered a Ship for all purposes"; `is_suit` honours it), `@skill_rewrite` ("all [Military] on your cards are treated as [Any Skill]"; `ctx.skills` applies it). Also `INCIDENTS_FROM_JUNK`, `CANNOT_PROMOTE`, `CANNOT_LOG` (effects that would log it do nothing: Rebelution), `WARP_DESTINATIONS` (a table card Ships can warp to, Earth), `PROTECTED_BEAMED` (cards beamed here cannot be recalled or dismissed, Earth) and `VP_SPECIAL[id] = fn(state, player, inst)` for asterisk VP. Pass `staging=True` for a SPECIAL that works from the Staging Area, or `staging="both"` to `@trait_modifier` for "while this card is in play". `INCIDENTS_FROM_LOG` is Pike's "find, free play or return Incident from your hand can also target your Log": `find`, `free_play_candidates` and `ctx.hand_incidents()` honour it, so card code that returns an Incident from hand picks from `ctx.hand_incidents()`. `player.enlisted` lists the Developments enlisted so far, for "have enlisted X" costs. `SHIP_WEIGHT[id] = 2` gives a Ship token weight 2 for securing and the Away Team placement check (A Fleet of 30 California-Class Ships, REQ-EXP-FRE-03). `RESOURCES_INTERCHANGEABLE` lets the owner spend Latinum as Dilithium and vice versa (D'Vana Tendi); `can_afford` and every Spend honour it. `DECK_FACE_UP` makes the owner's Draw deck public and lets them choose any card whenever an action draws, discards or looks at it (Gluonic Distortion). `@granted_play(source_id, index>=100, applies=..., text=..., uses=..., cost=...)` registers a PLAY that a card grants to other cards while it is in a table position (Deanna Troi-Riker gives every Incident one); the engine offers it beside the printed PLAYs |
| SPECIAL before final scoring | An `@operation` of kind SPECIAL, plus `BEFORE_SCORING.add(id)` | Runs at the start of final scoring wherever the owner has the card (Su'Kal) | No actions. Applies only while the card is in a table position |
| ENDGAME | `@endgame(ids)` function `score(state, player) -> int` | No actions. Queries only |
| Mission GOAL and REWARD | `@mission_goal(mission_id)` returning the contributing cards or None; `@mission_reward(mission_id, uses=...)` generator | One module per Captain: `engine/cards/<set>/missions_<captain>.py`. Mission ids come from `boards.yaml`. The engine offers completable missions in the Action Step (no action), then dismisses contributors that are beamed after the reward (REQ-MS-06) |
| Development cost | `development_cost(ids, *costs)` in the card's module | Resources and side effects such as "take an Incident". A Development without one cannot be enlisted |

`index` is the operation's position in the card spec, counting every printed operation. Identical copies in other decks register the same function by listing all their ids.

### File layout

```
server/content/cards/<set>.yaml         printed data per card: id, name, suit, traits, icons, VP, text
server/content/images/**/<id>.webp      processed image (card, board, command card), made by scripts/process_scans.py
server/engine/cards/<set>/<slug>.py     one module per card, linked to the data by card id
server/engine/cards/<set>/_util.py      shared read-only helpers for card modules; registers nothing, including the standard Ship operations (warp this ship, beam a card here)
server/engine/ops.py                    the operation runtime: Ctx queries, cost objects and the Actions implementations
server/engine/bot/<crew>.py             Automated Command rows for each Bot Crew
server/tests/test_<crew>.py             card tests per Crew deck, plus random-play smoke games
```

Card modules may only import from `engine.cards`, `engine.ops` (`A`, `Ctx`, the cost classes and helpers) and their set's `_util` (which has `owned_cards`, `table_of` and `ctx_for` for ENDGAME code, and Rebner's Helmet helpers: `is_helmet`, `wearing` for "if X is wearing a Helmet" (KW-HELM), `bareheaded_officers` and `beam_helmet_here`). A test enforces this.

### How a paused operation resumes

Generators cannot be saved, so the engine does not keep one between requests. When an operation starts, the engine snapshots the state. Each answer is appended to a list. To resume, the engine restores the snapshot and runs the operation again from the start, feeding the recorded answers. This is why card code must be deterministic. It also means objects held across a `yield` are rebuilt on each replay, so compare cards by `uid`, never by object identity, outside the operation.

### Examples

These are real card modules from Georgiou's deck.

```python
from engine.cards import operation, skill_icons
from engine.ops import A, DiscardFromHand, TakeIncidentCost

IDS = ("2GEO15", "2SOV17", "2ARC21", "2KIRK14", "3RIK19")  # Analyze and its identical copies


@operation(IDS, 0, uses=[A.GAIN_CARD], cost=[TakeIncidentCost()])
def gain_ship(ctx, actions):
    """PLAY: Take an Incident to gain a Ship."""
    yield from actions.gain_card(["Ship"], label="a Ship")


@operation(IDS, 1, uses=[A.GAIN_CARD], cost=[DiscardFromHand(2)])
def gain_cargo(ctx, actions):
    """PLAY: Discard 2 cards to gain a Cargo."""
    yield from actions.gain_card(["Cargo"], label="a Cargo")


# Lt. Detmer: a REACTION with a trigger, and a continuous PASSIVE.
@operation("2GEO21", 1, uses=[A.DRAW],
           trigger=lambda ctx, ev: ev["kind"] == "warp" and ev["seat"] == ctx.me.seat)
def draw_on_warp(ctx, actions):
    """REACTION: After warping a Ship, draw a card."""
    yield from actions.draw(1)


@skill_icons("2GEO21")
def any_skill(state, owner, inst):
    """PASSIVE: This card has 1 Any Skill."""
    return ["Any"]
```

The engine chooses targets by asking the player. Card code passes the legal candidates; it never picks one itself.

## The action list

These are the only actions card code may call. Each maps to a keyword in `requirements/14-keywords.md`. **Irreversible** means the action can reveal hidden information, use randomness or hand a choice to the opponent. The engine uses this column, together with each operation's `uses` list, to decide when to show the can't-be-undone warning (REQ-UNDO-11).

### Cards

| Action (`A.`) | Does | Keyword | Irreversible |
|---|---|---|---|
| `DRAW` | Draw from the Draw deck, cycling if empty | KW-DRW | Yes |
| `DRAW_FROM_DISCARD` | Take a matching card from the Discard pile to hand | KW-DRW-03 | No |
| `DISCARD` | Discard from hand, or the top card of your Draw deck (`discard_from_deck`, Chief Engineer) | KW-DIS | No |
| `DISMISS` | Move from play to the Discard pile | KW-DSM | No |
| `RECALL` | Move from play to hand | KW-REC | No |
| `DESTROY` | Return to the box | KW-DES | No |
| `LOG` | Move to the Captain's Log | KW-LOG | No |
| `BEAM` | Tuck a card under a Ship or Location | KW-BEAM | No |
| `PROMOTE` | Make a Person a Duty Officer. `as_person=True` promotes another card "as if it is a Person" (The Riker Maneuver) | KW-PROM | No |
| `DEPLOY` | Move a Ship or Ongoing card to the Fleet Area | KW-DEP | No |
| `PUT` | Put a card somewhere specific. Takes a `source`: hand by default, the Staging Area (a card putting itself, e.g. Class C Shuttlecraft), or the top of a named deck (the Supplement deck, Time Is Running Out). Takes a `destination`: top or bottom of the Draw deck (`put_on_deck(..., bottom=True)`: T'Ana), top of the Reserve deck ("Trip" Tucker III, Faith of the Heart), the Development pile (Ceti Eel), the Staging Area, the Status area (`put_into_status`: Gluonic Distortion goes into play when enlisted), or the top of the Bot deck. A card put into the Staging Area counts as put into play but its PLAY does not resolve. Putting onto an empty Reserve deck recreates it (REQ-CD-ARC-02) | KW-PUT, KW-PIP | No |
| `GIVE` | Give a card to the opponent | KW-GIVE | Yes |
| `TAKE_INCIDENT` | Take the top Incident into hand | KW-TAKE | Yes |
| `TAKE_ENCOUNTER` | Take an Encounter into hand. Takes `from`: top of the Encounter deck by default, or `bottom` (Messages from Old Friends) | KW-TAKE | Yes |
| `RETURN_INCIDENT` | Put an Incident on the bottom of the Incident deck | KW-RETI | No |
| `JUNK` | Move a card to the Junk pile. Takes a `source`: the Market by default, which refills the slot, never takes a card with tokens, and can be limited to `suits` (Joseph M'Benga's "Junk a Person from the Market"); your hand or Discard pile (Starbase 80); your Development pile (Knowledge of a Terrible Fate); or the top of the Incident deck (Time Is Running Out). Only the Market source refills | KW-JUNK | Yes |
| `GAIN_CARD` | Gain by suit or trait, including from the Junk | KW-GAIN | Yes |
| `SCAN` | Scan a number of cards of a suit | KW-SCAN-01 | Yes |
| `SCAN_FOR` | Scan for a trait or icon | KW-SCAN-05 | Yes |
| `FIND` | Search hand, Draw, Discard and Reserve for a card | KW-FIND | Yes |
| `ENLIST_RESERVE` | Top Reserve card to the top of the Draw deck | KW-ENRES | No |
| `ENLIST_DEVELOPMENT` | Pay for a Development and put it on the Draw deck. `pred` limits which (Even Bigger Helmet); `discount=True` pays 1 less Dilithium or 1 less Latinum (Rebner's Things That Make Us Smart) | KW-ENDEV | No |
| `FREE_PLAY` | Play a card without spending an action | KW-FREE | No |
| `DUPLICATE` | Resolve another card's operation as this card. Takes a `kind`: PLAY by default, or RESUPPLY (Una Chin-Riley). `skip_log_self=True` ignores any step of the copied operation that would log the duplicating card (Apergosians) | KW-DUP | No |
| `TAKE_FROM_REWARD_PILE` | Look at random Reward cards and take one | REQ-EXP-44 | Yes |
| `REVEAL` | Show cards from your hand to the opponent: the whole hand (Delta Vega, Lt. Saru) or chosen cards (Petra Aberdeen). The cards stay where they are; the client shows them to the opponent until the operation ends | — | Yes |
| `PEEK` | Look privately at the top card of a named deck, such as a Market deck, without taking it. Only the looking player sees it; the card stays on top (Sarina Douglas). `peek_deck` does the same for your own Draw deck (Deanna Troi-Riker) | — | Yes |
| `SWAP_JUNK_WITH_MARKET` | Exchange a card in the Junk with the faceup Market card of the same suit. The Market card goes to the Junk and the Junk card takes its slot. A Market card with tokens cannot be swapped (Plomeek Tea) | KW-JUNK-02 | No |
| `DRAW_FROM_LOG` | Take a card from your Captain's Log into hand (Shax, Search for Spock). Only when an effect says so; the Log is otherwise out of play | KW-LOG-05 | No |
| `SHUFFLE_INTO` | Shuffle a card into your Draw deck (`shuffle_into`: Second Contact, Dooplers), or shuffle the deck itself (`shuffle_deck`, Gluonic Distortion) | — | Yes |
| `REORDER` | Put cards you have looked at back on the top and/or bottom of their deck in an order you choose (Faith of the Heart). Used after `PEEK` | — | No |
| `TAKE_FROM_REINFORCEMENT` | Take a card of your choice from your Reinforcement pile into hand (Reinforce; solo campaign only) | REQ-CAMP-21 | No |

### Resources and actions

| Action (`A.`) | Does | Keyword | Irreversible |
|---|---|---|---|
| `GAIN_RESOURCE` | Gain Dilithium, Latinum or Glory. `supply=True` is Glory "from the supply", not from the Stardate card (Chateau Picard) | KW-GRES | No |
| `SPEND` | Spend as an effect, not a cost. Besides resources, it can spend available Action tokens, including "all remaining actions", which may be zero (Brad and Bradward Boimler) | KW-SPEND, KW-ACT | No |
| `PLACE_RESOURCES` | Put supply resources on a card | KW-PLACE | No |
| `MOVE_RESOURCES` | Move own resources onto a card | KW-MOVE | No |
| `STEAL` | Take resources from the opponent | KW-STEAL | No |
| `GAIN_ACTION` | Gain an extra action this turn | KW-ACT | No |
| `ADJUST_HAND_SIZE` | Change your hand size until the end of this turn (Betazed Intelligence). It resets when the turn ends | — | No |
| `GAIN_SPECIALTY` | Move a Specialty track. Positive amounts advance it; a negative amount moves it back (Dak'Rah's "lose 1 Military"), never below 0. The highest multiplier already reached is kept (REQ-SP-04) | REQ-SP-02 | No |
| `REMOVE_STARDATE_GLORY` | Remove Glory from the current Stardate card and return it to the supply (Kirk's and Pike's missions). If this empties the card, it is emptied as normal (REQ-SD-02) | REQ-SD-02 | No |

### Board and tokens

| Action (`A.`) | Does | Keyword | Irreversible |
|---|---|---|---|
| `WARP` | Move a Ship token to a Location | KW-WARP | No |
| `SEND_AWAY_TEAM` | Place Away Teams at a Location | KW-SEND | No |
| `ADD_AWAY_TEAM` | Move Away Team tokens from a player's set-aside supply onto their Captain, up to a maximum where stated (Archer's 4 set-aside teams: Commander Shran, Ambassador Soval, the Archer Bot's Vulcan / Andorian / Tellarite row). Unlike `SEND_AWAY_TEAM`, it increases the number of Away Teams in play | REQ-CD-ARC-01 | No |
| `REMOVE_AWAY_TEAM` | Remove Away Teams from a Location | KW-SEND | No |
| `TAKE_CONTROL` | Take control of a Location | KW-TC | Yes |
| `TRIGGER_CONTROL` | Resolve a Location's CONTROL again | KW-TRIG | No |
| `EXHAUST` | Exhaust an in-play card as an effect | KW-EXH | No |
| `REFRESH` | Refresh an in-play card | KW-REF | No |
| `MARK_TRAIT` | Khan only: mark a trait on the board | REQ-CD-KHN-06 | No |
| `FLIP_CARD` | Flip a double-sided card | REQ-CD-KHN-01 | No |

### Interaction

| Action | Does | Keyword | Irreversible |
|---|---|---|---|
| `actions.choose(...)`, `actions.may(...)` | Ask the right player to decide. Always available | — | No |
| `A.FORCE` | The opponent resolves an effect and makes its choices | KW-FORCE | Yes |
| `A.ATTACK` | Mark a part as the negative effect of an attack | KW-ATK | Yes |

### Bot actions (solo only)

Automated Command rows use the same action names. In a Bot context the engine supplies the Bot's version of each action, for example gain goes to the Bot Discard pile and take goes on the Bot deck (`requirements/22-solo-mode.md` §11). These extra actions exist only for Bot rows:

| Action (`A.`) | Does | Requirement |
|---|---|---|
| `EXPLORE` | Warp to the neutral Location with the fewest tokens | REQ-SOLO-164 |
| `ENGAGE` | Warp to the neutral Location with the most human tokens | REQ-SOLO-164 |
| `RESOLVE_CARD` | Resolve another Bot card, such as the top of the Bot deck | REQ-SOLO-100 |
| `CONTINUE_RESOLUTION` | Stop this row and resolve the next matching row | REQ-SOLO-120 |

### Changing the action list

- Add an action only when no existing action, or combination of actions, can express an effect.
- A new action must be general. It must not be named after a card or used by only one card, except the Khan and Bot actions above. `PEEK`, `REORDER`, `SHUFFLE_INTO` and `TAKE_FROM_REINFORCEMENT` have only one or two users today; they are written generally so later cards can reuse them.
- Adding an action means updating, in the same change: `server/engine/actions.py`, the tables in this file, its irreversible flag, and its tests.

## Tests

- Every card has a test module that exercises every one of its operations, including when costs cannot be paid.
- A registry test checks that:
  - every card in `server/content/cards/` has a module;
  - every printed operation has a function;
  - every `uses` list contains only actions from the action list;
  - card modules import only the allowed modules.
  - every printed operation and mission has code (`engine.cards.has_code`, `tests/test_registry.py`), except Khan's deck (on hold) and the solo-only cards that wait for the Bot.
- The engine enforces `uses` at runtime too. A test must fail if an operation calls an action it did not declare.
- Each acceptance scenario in `requirements/18-acceptance-scenarios.md`, `21-expansion-second-contact.md` §8 and `22-solo-mode.md` §13 has an engine test.
