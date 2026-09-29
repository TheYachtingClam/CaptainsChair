# Star Trek: Captain's Chair – Online Version Requirements

These documents turn the *Star Trek: Captain's Chair – To Boldly Go* rulebook (36 pages in [manual/base/](../manual/base/), `page-001.jpg` to `page-036.jpg`) into requirements for a digital, online implementation. They are organised by topic, not by page.

## Document map

| # | Document | Rulebook pages |
|---|---|---|
| 01 | [Game Overview, Resources & Win Conditions](01-game-overview.md) | 1, 8 |
| 02 | [Components (Data Model)](02-components.md) | 2–3 |
| 03 | [Central Setup](03-central-setup.md) | 4–5 |
| 04 | [Player Setup & Player Area](04-player-setup.md) | 6–7 |
| 05 | [Resupply and Control Steps](05-resupply-and-control.md) | 9 |
| 06 | [Action Step](06-action-step.md) | 10–11 |
| 07 | [Clean-up Step and Stardates](07-clean-up-step.md) | 12–13 |
| 08 | [Cards, Suits, Traits, Deck Management](08-cards-and-deck-management.md) | 14–16 |
| 09 | [Locations, Ships, Away Teams, Beaming](09-ships-locations-away-teams-beaming.md) | 18–19 |
| 10 | [Specialties and Missions](10-missions-and-specialties.md) | 17, 20, 27 |
| 11 | [Captain's Log and Hidden Information](11-logging-and-hidden-information.md) | 21 |
| 12 | [Component Anatomy (Card Schema)](12-component-anatomy.md) | 26–27 |
| 13 | [Final Scoring](13-final-scoring.md) | 24–25 |
| 14 | [Keywords in Detail](14-keywords.md) | 28–33 |
| 15 | [Crew Decks & Deck-Specific Rules](15-crew-decks.md) | 34–35 |
| 16 | [Cadet Training & Solo](16-solo-and-cadet-training.md) | 28 |
| 17 | [Quick Reference & Icons](17-reference-and-icons.md) | 36 |
| 18 | [Acceptance Scenarios](18-acceptance-scenarios.md) | Examples throughout |

## Conventions

- **Requirement IDs.** Rules use `REQ-<AREA>-<n>`. Keyword primitives use `KW-<KEYWORD>-<n>`.
- **Precedence.** Card text beats Keywords in Detail. Keywords in Detail beats the general rules. This rulebook beats the Core Box rulebook.
- **Server authority.** The server must enforce every rule and all hidden information. Clients only render state and send player choices.

## Known gaps and open questions

1. **Card content.** The rulebook shows only example cards. Every Crew deck and common card, about 280 cards, must be transcribed from the physical cards or a publisher list.
2. **Solo against the Bot.** Solo rules are in a separate rulebook that is not in this manual. Only Cadet Training mode can be specified now.
3. **Core Box compatibility.** Combining boxes, Burnham and *Recrystallize* depend on Core Box content that is not in this manual.
4. **Log visibility (resolved).** Page 21 calls Logs public, and page 31 says only the owner may look. The developers' errata lets the opponent ask about Log contents. The online game makes the Log viewable by both players with a click.
5. **Khan setup step number.** The Khan rules say "draw 6 cards in step 13 of player setup", but the opening hand is step 14. Treat it as the opening-hand step.
6. **Online features.** Lobby, matchmaking, reconnection, timers, undo policy and an action log are not covered by the rulebook. They need their own product requirements.
