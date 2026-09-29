# 12 – Component Anatomy (Card Data Schema)

Source: Rulebook pp. 26–27.

This file defines the data every card, board and token record must hold.

## 1. Crew and common cards

| Field | Description |
|---|---|
| `name` | Card name, top-left |
| `suit` | Card type, e.g. Captain, Person, Ship, Location, Directive |
| `traits[]` | 0–5 traits, top-right. Each has a category: species, special (Attack, Ongoing, Surprise, Wildcard) or regular |
| `skills[]` | Up to 3 Skill icons, upper-left: research, influence, military, any, variable |
| `focus` | Optional Focus icon, bottom-right: research, influence, military, best |
| `vp` | Printed Victory Points; may be negative; may carry an asterisk flag |
| `awayTeams` | Captain only. Number of Away Team tokens, with an optional "+" flag |
| `operations[]` | Ordered list of operations (see §2) |
| `devCost` | Development cards only. Resource costs and extra effects |
| `positionIndicator` | Available, Reserve, Development, Deployed, Controlled Location, Discard, Incident Deck, Starting Location, Advanced Location, Rewards, Solo Campaign, or none |
| `cardId` | Set code such as `2SOV01/24` |
| `deckIcon` | Owning Crew deck, or none for common cards |
| `boxMarker` | Optional `•` (duplicate) or `†` (replacement) |
| `shipToken` | Optional. Link to a Ship token record |
| `set` | Product the card comes from, e.g. To Boldly Go, Second Contact, Core Box |

## 2. Operations

Operations are colour-coded strips:

| Strip colour | Operation type |
|---|---|
| Grey / white | PLAY. May have an action cost and an ATTACK prefix |
| Blue | Table operations: ACTIVATION, PASSIVE, REACTION |
| Green | RESUPPLY or CLEAN-UP. CONTROL is also on Locations |
| Red | ENDGAME |
| Purple | SPECIAL, and SURPRISE (Bot only) |
| Dashed purple | SUPPORT (expansion) |
| Black | Development cost |

Each operation record needs:

- `type`
- `actionCost` (boolean, or a number when an effect costs several actions)
- `isAttack`
- `restriction` (Specialty and minimum level)
- `optional` flags for each "may" clause
- `effect` (see below)

- **REQ-AN-01** Effects must be expressed in a structured scripting format, a DSL or code hooks, that the rules engine can execute. Free text is for display only.
- **REQ-AN-02** Keep the printed rules text for every operation, to show in tooltips and card zoom.

## 3. Stardate cards

| Field | Description |
|---|---|
| `mode` | E.g. "2-PLAYER", "Cadet Training", solo |
| `sequence` | Order number, top-right |
| `whenEmptied` | Effect text and script |
| `stardateResolution` | Effect text and script |
| `startingGlory` | Glory placed when the card becomes topmost |
| `botActionCount` | Solo only |
| `id` | E.g. `SD09` |

## 4. Crew boards

See [10-missions-and-specialties.md](10-missions-and-specialties.md). Each board has a name, two sides, missions per side, a turn summary with the control limit and action count, and three tracks from 0 to 15 with multiplier positions.

## 5. Ship tokens

| Field | Description |
|---|---|
| `name` | Ship name |
| `deckIcon` | Owning Crew deck, or none for common |
| `cardRef` | The card the token belongs to |
| `weight` | How many Ships the token counts as for securing. Normally 1; 2 for *A Fleet of 30 California-Class Ships* |

## 6. Card backs (for UI rendering)

- Standard card back, used by Crew and Market decks.
- Common Location back.
- Captain back.
- Stardate backs.
- Status card back.

## 7. Automated Command cards (solo)

See [22-solo-mode.md](22-solo-mode.md) §6.

| Field | Description |
|---|---|
| `crew` | The Bot Crew it belongs to |
| `kind` | TRAITS, SUITS, KHAN IN EXILE, or FIVE YEAR MISSION: UPGRADES |
| `side` | For SUITS: WITH NO DUTY OFFICER or WITH DUTY OFFICER |
| `specialRule` | Optional Bot-specific rule shown at the top |
| `rows[]` | Ordered rows. Each has a trait list or suit, display text, and an effect script |
| `row.attackParts` | Which parts of the row are attacks (bold red) and which affect the human without attacking (bold) |
| `upgrades` | Upgrade cards only. WIN and LOSS sections, each with reinforceable card types and alternative bonuses |
