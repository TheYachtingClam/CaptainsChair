# Plan: the next tutorials

After *Learn to play with Picard* ([tutorial.md](tutorial.md)), tutorials go where the general rules stop helping: playing a real opponent, and the Captains whose decks change the rules. Agreed on 2026-10-29.

| Order | Tutorial | Kind | Plan |
|---|---|---|---|
| 1 | Playing against a Bot | Full: 3 guided turns, then tips | [tutorial-bot.md](tutorial-bot.md) |
| 2 | Khan (complexity 9) | Full | [tutorial-khan.md](tutorial-khan.md) |
| 3 | Rebner (8) | Full | [tutorial-rebner.md](tutorial-rebner.md) |
| 4 | Burnham (7) | Short: 1–2 guided turns | [tutorial-burnham.md](tutorial-burnham.md) |
| 5 | Captain primers (the rest) | One guided turn, then tips | [tutorial-primers.md](tutorial-primers.md) |

The 1–4 Captains (Picard, Georgiou, Shran, Soval, Koloth, Kirk, Sisko) play by the rules the Picard tutorial teaches. They get primers last, if at all.

## How each tutorial is made

The same four steps as the Picard tutorial, each tutorial on its own:

1. **Script, for your review.** I play the stacked game through in the engine, then write the steps, `more:` texts and tips. Every rule the text states is checked against the requirements and the engine. A replay test proves every scripted move.
2. **Framework additions it needs.** Listed in its plan; most are in the Bot tutorial's.
3. **Check.** The Playwright pass over every step on a phone and a laptop: text and icons shown, target visible, More opens. Then a full run to the end of the game.
4. **Deploy** when you say so. Then your play-through, and a revision from your notes.

## Shared framework work

Built with the first tutorial that needs each part. F1 to F5 are done (2026-10-29); F4 needed no new form, since Khan's mark answers have plain ids such as `ambassador|Ambassador`.

| # | What | Needed by |
|---|---|---|
| F1 | **Solo tutorials.** The script's setup names a Bot (`bot: {deck, difficulty}`), and `POST /api/tutorials/{id}` creates a solo game. | Bot |
| F2 | **More stacking.** The Bot deck and Supplement deck order (`bot_draw`, `bot_supplement`), the Encounter and Location deck tops, the Development pile's order, and Khan's Cadet `rival_captain`. All use no randomness, like the existing stack (REQ-TUT-10, -11). | Bot, Khan, Rebner |
| F3 | **Coaching during the Bot's turn.** Steps can point at the Bot's playback panel and the matched row on its command card (`show: bot-panel`, `show: bot-row`). Next steps work while the panel plays. The panel's Done stays the player's own button, not a scripted move. | Bot |
| F4 | **New `expect` forms**, if the decks' answers need them, such as Khan's trait marks. Each one is checked against the engine's option ids before it is used. | Khan, Rebner |
| F5 | **Finding the tutorials.** The lobby groups them: *Learn to play* (Picard, then the Bot) and *Captains*. The New Game screen shows "New to Khan? Try the tutorial" beside a Captain that has one. Scripts get `group` and `captain` fields. | Khan |
| F6 | **Where players stop** (optional): for each tutorial, the admin page shows how many players reached each step. It shows which steps to rewrite. | Any |

## Requirements

Each tutorial gets a section in [requirements/24-tutorials.md](../requirements/24-tutorials.md) (§3 onwards) when its script is written. F1–F6 go into §1.
