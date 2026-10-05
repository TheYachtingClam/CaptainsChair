# Open questions from card specs

Collected from the "Rulings and open questions" sections of every card, board and command-card spec under `resources/scans/`. Each needs a decision before the code that depends on it is written.

## Rules questions

- **cb-khan** ([to_boldly_go/boards/cb-khan.md](to_boldly_go/boards/cb-khan.md)): The second mission's reward flips the Captain. This is a second flip trigger besides Ceti Alpha VI; confirm whether both apply.
- **Ceti Alpha VI** ([to_boldly_go/cards/captains/kahn/2KHA03.md](to_boldly_go/cards/captains/kahn/2KHA03.md)): Starts in play. Logging it is what flips Khan's Captain to Wrathful Khan (REQ-CD-KHN-01). Open question: the card text flips only Ceti Alpha V; confirm when the Captain flips.
- **Cmdr. Burnham in Cadet Training** ([to_boldly_go/cards/captains/georgiou/2GEO13.md](to_boldly_go/cards/captains/georgiou/2GEO13.md)): Her attack forces the opponent to log a Duty Officer, or dismiss one so you gain 3 Glory. The virtual opponent has one Duty Officer (REQ-CTM-12) but the rules don't say which option it picks. Implemented as: it logs, so you gain nothing. Confirm.
- **Core Box Burnham variant** (REQ-CTM-21): The rule refers to a Burnham Status card, but no Crew deck with that card is in the content yet. Not implemented.
- **Ambassador Gral against an ignored attack** ([to_boldly_go/cards/person/2PER02.md](to_boldly_go/cards/person/2PER02.md)): His Reaction gives an Incident instead of returning it, and is an attack. If the opponent ignores it (Riva), the rules don't say what happens to the Incident. Implemented as: it is returned as normal. Confirm.
- **Attacks against the Cadet virtual opponent** (REQ-CTM-12): Implemented as: each attack works once against its "one of everything". Stealing takes 1 from the supply, removing Away Teams removes 1 (1 Glory for the Disruptor Pistols), and dismissing its Duty Officer still pays (2 Glory for Ash Tyler). Effects that only hurt it do nothing. Confirm.
- **Wildcard choice** (REQ-TR-07): The rules let the owner decide each time whether a Wildcard counts as the trait. Implemented as: your own Wildcard always counts for your own effects, without a prompt. This only matters when counting hurts you, for example the Universal Translator dismissing your Alien Ships. Confirm, or ask for a prompt in those cases.

## Gaps in the CLAUDE.md action list

None. Every action named in the specs is in the CLAUDE.md action list.
