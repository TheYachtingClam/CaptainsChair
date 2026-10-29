# Plan: "Playing against a Bot"

The second tutorial ([tutorials-roadmap.md](tutorials-roadmap.md)). The Picard tutorial's last tip already sends players here.

## What the player should know at the end

- How a solo game is set up: the Bot's deck, its Supplement deck, its SUITS card and Automated Command cards, and the difficulty's Stardate cards with their Bot actions.
- How to read the Bot's turn in the playback panel: which card it flipped, which row matched, and what it did.
- How the Bot resolves a card: SURPRISE first, then the TRAITS rows top to bottom, then the suit row on the SUITS side face up (REQ-SOLO-100 onwards).
- The Bot as a real opponent:
  - its Away Teams and Ships contest your Locations, so securing means 2 more tokens than it has;
  - your Ships keep its Away Teams out (KW-SEND-03);
  - its taking control dismisses your Ships there.
- Attacks: the bold parts of a row are aimed at you. Your "when attacked" Reactions can answer them. Reactions that trigger on its turn wait for your next turn (REQ-AS-34).
- Its Duty Officer flips the SUITS card.
- How it scores at the end.

## Decisions

1. **You play Picard**, the deck you already know, so every new thing on screen is about the Bot.
2. **The Bot: Ensign difficulty**, so it is clearly beatable. Which Crew is decided in step 1, after reading the command cards: it should attack early and have readable rows. Koloth (complexity 3) is the first candidate, Shran the second.
3. **3 guided turns each, then free play with tips**, as before. The stacked Bot deck makes its first three turns show, in order: a gain, an attack, and a Location contest.
4. **Not taught here:** the Five-Year Mission campaign and the Ticking Clock (a tip points at them at the end).

## Steps

1. ✅ **Script** (for your review; `server/content/tutorials/bot-basics.yaml`, 54 steps, Koloth chosen): choose the Bot, then stack your deck and the Bot's so its first turns show the lessons above. Write the steps, More texts and tips (its first SURPRISE card, its Duty Officer, the Bot deck reshuffling with a Supplement card, your first attack held for your turn, final scoring with the Bot's ENDGAME values).
2. ✅ **Framework:** F1 (solo tutorials), F2 (Bot deck stacking), F3 (coaching during the Bot's turn).
3. ✅ **Check:** the Playwright pass on phone and laptop, including steps shown during the Bot's playback (the coach moves below the Bot's panel on a laptop).
4. **Deploy** on your word.

## Risks

- **The Bot's turns must replay exactly.** They are run without stored commands, so the stacked decks and the seed fully decide them; the replay test checks the Bot's first three turns card by card.
- **The playback panel and the coach on a phone.** Both want the bottom of the screen. During the Bot's turn the coach may need to sit above the panel; this is settled in step 3.
