# Star Trek: Captain's Chair – Online Version Requirements

These documents turn the *Star Trek: Captain's Chair – To Boldly Go* rulebook (36 pages in [manual/base/](../manual/base/), `page-001.jpg` to `page-036.jpg`) into requirements for a digital, online implementation. They also cover the *Second Contact* expansion ([manual/expansion/](../manual/expansion/), 6 pages) and the solo rulebook ([manual/solo/](../manual/solo/), 21 pages). Page numbers refer to the base rulebook unless a file says otherwise. They are organised by topic, not by page.

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
| 16 | [Cadet Training](16-solo-and-cadet-training.md) | 28 |
| 17 | [Quick Reference & Icons](17-reference-and-icons.md) | 36 |
| 18 | [Acceptance Scenarios](18-acceptance-scenarios.md) | Examples throughout |
| 19 | [Technical Architecture: Python API, React Client, Password Access](19-technical-architecture.md) | Not from the rulebook |
| 20 | [Undo](20-undo.md) | Not from the rulebook |
| 21 | [Expansion: Second Contact](21-expansion-second-contact.md) | Expansion pp. 1–6 |
| 22 | [Solo Mode: Playing Against the Bot, and the Five-Year Mission Campaign](22-solo-mode.md) | Solo rulebook pp. 1–21 |

## Conventions

- **Requirement IDs.** Rules use `REQ-<AREA>-<n>`. Keyword primitives use `KW-<KEYWORD>-<n>`.
- **Precedence.** Card text beats Keywords in Detail. Keywords in Detail beats the general rules. This rulebook beats the Core Box rulebook.
- **Server authority.** The server must enforce every rule and all hidden information. Clients only render state and send player choices.

## Known gaps and open questions

1. **Card content.** The rulebook shows only example cards. Every Crew deck and common card, about 280 cards, must be transcribed from the physical cards or a publisher list.
2. **Solo against the Bot (resolved).** The solo rulebook is now covered in [22-solo-mode.md](22-solo-mode.md). The Automated Command card rows for each Bot Crew still have to be transcribed from the physical cards, like all other card text.
3. **Core Box compatibility.** Combining boxes, Burnham and *Recrystallize* depend on Core Box content that is not in this manual.
4. **Log visibility (resolved).** Page 21 calls Logs public, and page 31 says only the owner may look. The developers' errata lets the opponent ask about Log contents. The online game makes the Log viewable by both players with a click.
5. **Khan setup step number.** The Khan rules say "draw 6 cards in step 13 of player setup", but the opening hand is step 14. Treat it as the opening-hand step.
6. **Online features.** Lobby, reconnection, the action log and access control are now covered in [19-technical-architecture.md](19-technical-architecture.md). Undo is part of the first version and is specified in [20-undo.md](20-undo.md). Matchmaking, timers and spectators are out of scope for the first version.
