# Card spec format

Every card scan has a spec file next to it with the same name and a `.md` extension, for example `to_boldly_go/cards/captains/soval/2SOV01.jpg` and `2SOV01.md`. A command-card PDF has one spec covering all its sides, for example `command/cc-soval.md`.

A card spec holds everything needed to use the card in the game and to write its code under the rules in `CLAUDE.md`. It is the card's requirements document. Card code and card data are generated from it, so when the two disagree, fix the spec first.

## Layout

```markdown
---
id: 2SOV01                  # printed card id, without the "/24" count
name: Soval
suit: Captain               # Person, Cargo, Ship, Ally, Encounter, Incident, Location, Directive, Captain, Status, Stardate
set: to_boldly_go           # base_game (the Core Box), to_boldly_go, second_contact, promo1, promo2
deck: soval                 # Crew deck id, or common
set_code: 2SOV01/24         # exactly as printed at the bottom
position: null              # position indicator as printed: Available, Reserve, Development, Deployed,
                            # Controlled Location, Discard, Incident Deck, Starting Location,
                            # Advanced Location, Rewards; null if none
traits: [Vulcan, Telepath, Ambassador]   # in printed order
skills: []                  # Skill icons, upper left: Research, Influence, Military, Any, Variable
focus: null                 # Focus icon, bottom right: Research, Influence, Military, Best
vp: null                    # printed VP; negative allowed; "3*" when it has an asterisk
away_teams: 4               # Captain only, e.g. 4 or "2+"
development_cost: null      # Development cards only, as printed
ship_token: false           # true when the card has a Ship token
box_marker: null            # "duplicate" (• after the set code), "replacement" (†), or null.
                            # Used when combining boxes (REQ-CS-31)
same_as: null               # optional: the id of an identical card in another set or deck, e.g. the To Boldly
                            # Go reprint of a Core Box card. The two share one card module, and
                            # scripts/build_content.py checks that their printed data match
replaced_by: null           # optional: on an old Core Box version, the id of the To Boldly Go card that replaces it
scan: 2SOV01.jpg
---

# Soval

## Printed text

Verbatim card text, one operation per line, with icons written as [Icon] (see the legend below).

## Operations

One subsection per printed operation, in printed order.

### 1. ACTIVATION

- **Printed:** the operation's text.
- **Action cost:** yes or no.
- **Attack:** yes or no.
- **Requires:** Specialty or other precondition, or none.
- **Cost:** everything that must be paid or done before the effect ("A" in "do A to do B"), or none.
- **Trigger:** for REACTION, SUPPORT and triggered PASSIVE operations, the exact event; otherwise omit.
- **Effect:** numbered steps, in order.
- **Choices:** every decision, and which player makes it.
- **Actions used:** the action names from `CLAUDE.md`, e.g. `DISMISS`, `DRAW`.
- **Undoable:** no if any action used is marked irreversible in `CLAUDE.md`; otherwise yes.
- **Rules:** requirement and keyword ids that govern it, e.g. KW-DSM, REQ-AS-20.

## Scoring

Printed VP, Focus icon, ENDGAME operation and any asterisk rule.

## Solo

How the Bot handles the card: its SURPRISE operation if it has one, otherwise
"resolved through the Automated Command cards by trait and suit".

## Rulings and open questions

Interpretations made while writing the spec, and anything that needs a decision.

## Tests

Given / When / Then cases for every operation, including when a cost cannot be paid.
```

Sections with nothing to say keep their heading with "None."

## Extra fields for Stardate cards

Stardate specs add these frontmatter fields, and describe their two effects as the operations `WHEN EMPTIED` and `STARDATE RESOLUTION`:

| Field | Meaning |
|---|---|
| `mode` | The mode printed at the top, e.g. `2-Player`, `Solo Cadet Practice`, `Solo vs Admiral Bot` |
| `sequence` | Position in its pile, 1 on top |
| `starting_glory` | Glory placed on it when it becomes the top card |
| `bot_actions` | Solo only: cards the Bot draws in its Action Step |

## Command-card specs

`<set>/command/cc-<captain>.md` covers all four sides of one Bot Crew's Automated Command cards. Each side is a table with one row per printed row: what it matches, the printed text, numbered steps, the actions used, and whether it can be undone. Bot rows also use the Bot-only actions in `CLAUDE.md`: `EXPLORE`, `ENGAGE`, `RESOLVE_CARD` and `CONTINUE_RESOLUTION`.

## Open questions

`OPEN_QUESTIONS.md` collects every open question and action-list gap from the specs. Regenerate it after editing specs.

## Icon legend

| Written as | Icon |
|---|---|
| [Research], [Influence], [Military] | Skill icons. Inline in text they are tabs with a rounded right edge. Plain outline icons with no box mean the Specialty track itself, as in "Gain 1 [Research]" |
| [Research Focus], [Influence Focus], [Military Focus] | Focus icons. Inline in text they have a folded corner at the bottom right |
| [Any Skill] | Skill icon counting as any one Specialty |
| [Best Focus] | Focus icon scoring the best multiplier |
| [Dilithium], [Latinum], [Glory] | Resources (purple crystal, gold bar, blue token) |
| [Action] | The action cost icon (stylus) |
| [Away Team] | Away Team token |
| [VP] | Victory Points |

Suits and traits are written by name with a capital letter, as they appear on the card's badges, for example "Dismiss a Human".
