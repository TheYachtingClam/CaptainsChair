# Open questions from card specs

Collected from the "Rulings and open questions" sections of every card, board and command-card spec under `resources/scans/`. Each needs a decision before the code that depends on it is written.

## Rules questions

- **cb-khan** ([to_boldly_go/boards/cb-khan.md](to_boldly_go/boards/cb-khan.md)): The second mission's reward flips the Captain. This is a second flip trigger besides Ceti Alpha VI; confirm whether both apply.
- **Ceti Alpha VI** ([to_boldly_go/cards/captains/kahn/2KHA03.md](to_boldly_go/cards/captains/kahn/2KHA03.md)): Starts in play. Logging it is what flips Khan's Captain to Wrathful Khan (REQ-CD-KHN-01). Open question: the card text flips only Ceti Alpha V; confirm when the Captain flips.
- **Cmdr. Burnham in Cadet Training** ([to_boldly_go/cards/captains/georgiou/2GEO13.md](to_boldly_go/cards/captains/georgiou/2GEO13.md)): Her attack forces the opponent to log a Duty Officer, or dismiss one so you gain 3 Glory. The virtual opponent has one Duty Officer (REQ-CTM-12) but the rules don't say which option it picks. Implemented as: it logs, so you gain nothing. Confirm.
- **Core Box Burnham variant** (REQ-CTM-21): The rule refers to a Burnham Status card, but no Crew deck with that card is in the content yet. Not implemented.

## Gaps in the CLAUDE.md action list

None. Every action named in the specs is in the CLAUDE.md action list.
