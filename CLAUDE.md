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
```

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
5. **Card code never decides for a player.** Every choice, including every "may", goes through `actions.choose(...)` or `actions.may(...)`. The engine asks the right player, or applies the Bot rules in solo games. These two are always available and need no declaration.
6. **Every action is a generator. Call it with `yield from`.** Any action can pause the operation for a player decision, for example a Reaction, a Wildcard choice or enlisting a Development during a reshuffle. `yield from` lets the engine suspend and resume the operation.
7. **Reading is free.** Read the game through `ctx`, the read-only query object: traits in play, token counts, tracks, zones, `ctx.this_card`, `ctx.me`, `ctx.opponent`. Queries need no declaration and never change state.
8. **Costs and requirements are declarative.** Put costs in `cost=`, including the action cost, and Specialty requirements in `requires=`. The engine checks them to decide whether the operation is legal, and pays the costs before running the body. The body contains effects only. An operation whose cost cannot be paid can never start (REQ-AS-04, KW-REQ-02).
9. **Attacks are marked.** Set `attack=True` on ATTACK operations. Wrap each part that targets the opponent in `yield from actions.attack(...)`, so the engine can apply cancellation and "ignore the negative effect" rules correctly (KW-ATK-03, REQ-SOLO-184).
10. **"This card" means `ctx.this_card`.** Never hard-code a card identity for "this card". Duplicate effects rely on it pointing at the duplicating card (KW-DUP-04).
11. **One file per card.** Never put card-specific logic in the engine core, and never add an action named after a card.

### Operation kinds

| Kind | Function shape | Notes |
|---|---|---|
| PLAY, ACTIVATION, CONTROL, RESUPPLY, CLEAN-UP, SPECIAL, SURPRISE, SUPPORT | Generator using `actions` | ACTIVATION and REACTION exhaust automatically. Do not declare exhaust as a cost |
| REACTION, triggered PASSIVE, SUPPORT | Generator plus `trigger=` | Triggered PASSIVEs are mandatory. REACTION and SUPPORT are offered to the player |
| Continuous PASSIVE | `modifiers(ctx) -> list[Modifier]` | No actions. Examples: hand size, extra Duty Officer, "treated as" |
| ENDGAME | `score(ctx) -> int` | No actions. Queries only |
| Mission GOAL | `goal(ctx) -> bool` | Queries only. The REWARD is a normal generator |
| Development cost | `cost=` on the card | Resources and side effects such as "take an Incident" |

### File layout

```
server/content/cards/<set>.yaml         printed data per card: id, name, suit, traits, icons, VP, text
server/content/images/**/<id>.webp      processed image (card, board, command card), made by scripts/process_scans.py
server/engine/cards/<set>/<slug>.py     one module per card, linked to the data by card id
server/engine/actions.py                the action list and its implementations
server/engine/bot/<crew>.py             Automated Command rows for each Bot Crew
server/tests/cards/<set>/test_<slug>.py one test module per card
```

Card modules may only import from `engine.cards`, `engine.actions`, `engine.costs`, `engine.queries` and `engine.types`.

### Examples

These show the shape of the code. The card ids are placeholders; use the ids printed on the real cards.

```python
from engine.cards import card, operation
from engine.actions import A
from engine.costs import ActionCost, Spend, DiscardFromHand
from engine.types import Suit, Zone


@card("2GEO??")  # Class C Shuttle
class ClassCShuttle:
    # PLAY (costs an action): Send an Away Team to a Location where you have a Ship.
    @operation("PLAY", cost=[ActionCost()], uses=[A.SEND_AWAY_TEAM])
    def send_team(ctx, actions):
        targets = ctx.locations(where=lambda loc: ctx.ships_at(loc, owner=ctx.me))
        yield from actions.send_away_team(to=targets)


@card("2LOC??")  # Denaxi Depot
class DenaxiDepot:
    # ACTIVATION: Spend 1 Latinum and discard a card to find a Ship,
    # except in your Reserve deck.
    @operation("ACTIVATION", cost=[Spend(latinum=1), DiscardFromHand(1)], uses=[A.FIND])
    def find_ship(ctx, actions):
        yield from actions.find(suit=Suit.SHIP, exclude=[Zone.RESERVE])


@card("2ALL??")  # Bynars
class Bynars:
    # PLAY: Gain a Cargo. Log this card.
    @operation("PLAY", uses=[A.GAIN_CARD, A.LOG])
    def gain_cargo(ctx, actions):
        yield from actions.gain_card(suit=Suit.CARGO)
        yield from actions.log(ctx.this_card)
```

The engine chooses targets by asking the player. Card code passes the legal candidates; it never picks one itself.

## The action list

These are the only actions card code may call. Each maps to a keyword in `requirements/14-keywords.md`. **Irreversible** means the action can reveal hidden information, use randomness or hand a choice to the opponent. The engine uses this column, together with each operation's `uses` list, to decide when to show the can't-be-undone warning (REQ-UNDO-11).

### Cards

| Action (`A.`) | Does | Keyword | Irreversible |
|---|---|---|---|
| `DRAW` | Draw from the Draw deck, cycling if empty | KW-DRW | Yes |
| `DRAW_FROM_DISCARD` | Take a matching card from the Discard pile to hand | KW-DRW-03 | No |
| `DISCARD` | Discard from hand | KW-DIS | No |
| `DISMISS` | Move from play to the Discard pile | KW-DSM | No |
| `RECALL` | Move from play to hand | KW-REC | No |
| `DESTROY` | Return to the box | KW-DES | No |
| `LOG` | Move to the Captain's Log | KW-LOG | No |
| `BEAM` | Tuck a card under a Ship or Location | KW-BEAM | No |
| `PROMOTE` | Make a Person a Duty Officer | KW-PROM | No |
| `DEPLOY` | Move a Ship or Ongoing card to the Fleet Area | KW-DEP | No |
| `PUT` | Put a card somewhere specific, such as the top of the Draw deck or the Staging Area. Takes a `source`: hand by default, or the Staging Area when a card puts itself (Class C Shuttlecraft). A card put into the Staging Area counts as put into play but its PLAY does not resolve | KW-PUT, KW-PIP | No |
| `GIVE` | Give a card to the opponent | KW-GIVE | Yes |
| `TAKE_INCIDENT` | Take the top Incident into hand | KW-TAKE | Yes |
| `TAKE_ENCOUNTER` | Take an Encounter into hand | KW-TAKE | Yes |
| `RETURN_INCIDENT` | Put an Incident on the bottom of the Incident deck | KW-RETI | No |
| `JUNK` | Move a card to the Junk pile. Takes a `source`: the Market by default, which refills the slot and never takes a card with tokens; or your hand or Discard pile, which does not refill (Starbase 80) | KW-JUNK | Yes |
| `GAIN_CARD` | Gain by suit or trait, including from the Junk | KW-GAIN | Yes |
| `SCAN` | Scan a number of cards of a suit | KW-SCAN-01 | Yes |
| `SCAN_FOR` | Scan for a trait or icon | KW-SCAN-05 | Yes |
| `FIND` | Search hand, Draw, Discard and Reserve for a card | KW-FIND | Yes |
| `ENLIST_RESERVE` | Top Reserve card to the top of the Draw deck | KW-ENRES | No |
| `ENLIST_DEVELOPMENT` | Pay for a Development and put it on the Draw deck | KW-ENDEV | No |
| `FREE_PLAY` | Play a card without spending an action | KW-FREE | No |
| `DUPLICATE` | Resolve another card's operation as this card | KW-DUP | No |
| `TAKE_FROM_REWARD_PILE` | Look at random Reward cards and take one | REQ-EXP-44 | Yes |
| `REVEAL` | Show cards from your hand to the opponent: the whole hand (Delta Vega, Lt. Saru) or chosen cards (Petra Aberdeen). The cards stay where they are; the client shows them to the opponent until the operation ends | — | Yes |
| `PEEK` | Look privately at the top card of a named deck, such as a Market deck, without taking it. Only the looking player sees it; the card stays on top (Sarina Douglas) | — | Yes |
| `SWAP_JUNK_WITH_MARKET` | Exchange a card in the Junk with the faceup Market card of the same suit. The Market card goes to the Junk and the Junk card takes its slot. A Market card with tokens cannot be swapped (Plomeek Tea) | KW-JUNK-02 | No |

### Resources and actions

| Action (`A.`) | Does | Keyword | Irreversible |
|---|---|---|---|
| `GAIN_RESOURCE` | Gain Dilithium, Latinum or Glory | KW-GRES | No |
| `SPEND` | Spend as an effect, not a cost | KW-SPEND | No |
| `PLACE_RESOURCES` | Put supply resources on a card | KW-PLACE | No |
| `MOVE_RESOURCES` | Move own resources onto a card | KW-MOVE | No |
| `STEAL` | Take resources from the opponent | KW-STEAL | No |
| `GAIN_ACTION` | Gain an extra action this turn | KW-ACT | No |
| `GAIN_SPECIALTY` | Advance a Specialty track | REQ-SP-02 | No |

### Board and tokens

| Action (`A.`) | Does | Keyword | Irreversible |
|---|---|---|---|
| `WARP` | Move a Ship token to a Location | KW-WARP | No |
| `SEND_AWAY_TEAM` | Place Away Teams at a Location | KW-SEND | No |
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
- A new action must be general. It must not be named after a card or used by only one card, except the Khan and Bot actions above. `PEEK` and `SWAP_JUNK_WITH_MARKET` each have one user today; they are written generally so later cards can reuse them.
- Adding an action means updating, in the same change: `server/engine/actions.py`, the tables in this file, its irreversible flag, and its tests.

## Tests

- Every card has a test module that exercises every one of its operations, including when costs cannot be paid.
- A registry test checks that:
  - every card in `server/content/cards/` has a module;
  - every printed operation has a function;
  - every `uses` list contains only actions from the action list;
  - card modules import only the allowed modules.
- The engine enforces `uses` at runtime too. A test must fail if an operation calls an action it did not declare.
- Each acceptance scenario in `requirements/18-acceptance-scenarios.md`, `21-expansion-second-contact.md` §8 and `22-solo-mode.md` §13 has an engine test.
