# Plan: solo mode against the Bot

Solo mode is the *Starfleet Command Training Program*: one player against an automated opponent, the Bot ([requirements/22-solo-mode.md](../requirements/22-solo-mode.md)). The Bot ignores its card text. It resolves each card with its Crew's two Automated Command cards, using the card's traits and suit. On top of that sits the Five-Year Mission, a campaign of up to 10 solo games with promotions and deck upgrades.

This plan builds it one step at a time, like [card-implementation.md](card-implementation.md). Each step ends with something you can test, and nothing in a later step is needed to test an earlier one.

## How every step works

The same loop as the card plan:

1. **Before coding:** list the rulings the step needs and record any new question in `resources/scans/OPEN_QUESTIONS.md`. Stop only when no sensible default exists.
2. **Build:** engine first, then the Bot rows or card code, then the client.
3. **Automated tests:**
   - one test per case in each command-card spec's Tests section;
   - the registry test, extended to Bot rows;
   - random games against the step's Bots, so every row runs at least once.
4. **Your test:** rebuild Docker and play the step's Bots in the browser. Each step lists what to try.
5. **Finish:** update CLAUDE.md if the runtime changed, report, and wait for your go-ahead. You commit.

## Status today

| Piece | State |
|---|---|
| Solo Stardate cards, 5 difficulties | In the content, with Bot actions per card. Not used yet |
| Automated Command card specs | Written for all 8 Crews plus Khan, in `resources/scans/<set>/command/`: about 21 rows per Crew, plus the campaign upgrade card. Images processed. Not yet in `server/content/` |
| SURPRISE operations | 3 to write: *Dilithium Shockwave*, *Knowledge of a Terrible Fate*, *Time Is Running Out*. Khan's 4 wait with Khan |
| Solo Directive *Reinforce* | Not written. Campaign only |
| Engine | Has `GameMode` "solo" in the API schema, but `new_game` rejects it. No Bot, no value function |
| Client | No solo option in New Game, no Bot area |
| Campaign | Nothing yet: no storage, no screens |

## Design decisions

These shape every step. Each has a recommended default, which I'll use unless you say otherwise.

1. **The Bot runs inside the engine.**
   - The Bot's turn is part of the turn loop (`advance`). It runs every Bot step itself, and only stops when the human has to decide something, such as which Away Team a Bot attack removes.
   - The server still stores only the seed and the human's commands. Replay and undo keep working unchanged, and the Bot needs no access to hidden information.
   - This meets REQ-SRV-17's intent (the Bot runs on the server with the same engine) without making it a separate command source. I'll update that requirement to say so.
2. **The Bot is a normal player in the state.**
   - It is the second entry in `state.players`, marked as a Bot, with a small `bot` record: Crew, difficulty, which SUITS side is up, Ticking Clock, and the stack of cards being resolved.
   - Its zones reuse the player zones:

     | Bot zone | Player zone it uses |
     |---|---|
     | Bot deck | `draw` |
     | Supplement deck | `reserve` |
     | Bot Discard pile | `discard` |
     | Staging Area | `staging` |
     | Control Area | `duty`, `locations` and `fleet` |
     | Log | `log` |
     | Hand | always empty |

   - So human card code that says "your opponent" keeps working, through `ctx.opponent`.
3. **Bot rows are code, like card operations** (CLAUDE.md "Card effects are code"; REQ-SOLO-83).
   - Each row is one function in `server/engine/bot/<crew>.py`, registered with `@row(crew, card, number, matches=..., uses=...)`.
   - It receives Bot versions of the actions. For example, *gain* goes to the Bot Discard pile and *take* goes on top of the Bot deck, both picking the most valuable card. The Bot-only actions (`EXPLORE`, `ENGAGE`, `RESOLVE_CARD`, `CONTINUE_RESOLUTION`) are already in the CLAUDE.md action list.
   - The printed row text goes into `server/content/command.yaml` for display and the log, built from the specs by `scripts/build_content.py`.
4. **Human card effects aimed at the Bot go through one hook** in the actions, not per card. That hook handles:
   - forced choices: the Bot picks the first legal option;
   - Incidents: the Bot declines to return them;
   - draws: "draw a card" discards the top card of the Bot deck instead;
   - steals: they come from the supply;
   - attacks on the hand: the human decides whether they succeeded.

   Existing card modules shouldn't need changes.
5. **Watching the Bot is client-side.**
   - The engine runs the whole Bot turn at once and logs each step in plain words (REQ-SOLO-05): which card was flipped, which row matched and why, and what each step did.
   - The client replays those log entries one at a time, with Next, Auto-play and Skip (REQ-SOLO-56).
6. **Khan stays out**, as in the card plan. His Bot depends on the same open questions as his deck. The Khan Bot and his SURPRISE cards join when Khan does.
7. **Campaigns belong to a campaign link.** The server has no accounts, only a shared password. So a campaign gets its own secret link, stored as a token hash like seat tokens, which you can bookmark (REQ-CAMP-54).

---

## Step 1: A solo game with a placeholder Bot (done)

Everything except the Automated Command rows. The Bot plays real turns, but every card it resolves just goes to its Discard pile with a "no row yet" note.

- **Content:**
  - `build_content.py` reads the command-card specs into `server/content/command.yaml`, with each side's rows: number, matched traits or suit, printed text, and attack parts.
  - `content().command` loads it.
- **Setup** (REQ-SOLO-20 to -33):
  - the difficulty's Stardate cards;
  - the human goes first;
  - the Bot has no actions, mission tokens or resources;
  - the Bot deck, with Deployed and Controlled Location cards on top, and the Supplement deck (Developments under Reserves);
  - Status cards removed;
  - Incident-deck cards shuffled in;
  - the Bot's Away Teams;
  - both command cards, starting on TRAITS and SUITS WITH NO DUTY OFFICER.
- **The value function** (REQ-SOLO-40 to -43): one function, with parameters for whose multipliers to use and whether to pick the most or least valuable. It handles the tie-breaks: more tokens first, then leftmost; for the Junk, most recent first.
- **The Bot's turn:**
  - no Resupply;
  - the Control Step takes its most valuable secured Location;
  - the Action Step draws as many cards as the current Stardate's Bot actions;
  - the Clean-up resolves a held Stardate, discards the Staging Area, and places Glory on the Market card least valuable to the human.
- **Deck rules:** the Bot deck reshuffles from its Discard pile, then takes the top Supplement card.
- **Ending and scoring** (REQ-SOLO-70 to -73):
  - the game always ends with a Bot turn;
  - the Bot scores 5 VP per ENDGAME it owns, 1 VP per 2 Dilithium plus Latinum, and asterisk VP;
  - a tie or the Burn is a loss for the human.
- **Server:** game creation accepts the Bot's Crew, difficulty and Ticking Clock, and starts at once (REQ-SRV-18, -19).
- **Client:**
  - New Game gets a solo option, and suggests Cadet Training to first-time players (REQ-SOLO-04);
  - the Bot gets a play area: Bot deck and Supplement counts, Staging Area, Control Area, Discard pile, Log, tracks and Glory;
  - the two command cards are shown with the face-up sides.

**You test:** start a solo game against any Bot at any difficulty. Play your turns and watch the Bot draw its cards, place Glory and reshuffle. Then play to the end and check the score breakdown and the win or loss.

## Step 2: The Bot runtime, with the Soval Bot (done)

The engine that resolves Bot cards, proven on one Crew. Soval comes first because the solo rulebook's full Bot turn uses him.

- **Matching** (REQ-SOLO-82, -87, -120, -121):
  - a Surprise card resolves its SURPRISE operation;
  - otherwise the first TRAITS row with one of the card's traits matches, and a Wildcard card matches the first trait row;
  - otherwise the card's suit row on the face-up SUITS side;
  - "Continue resolution" moves on to the next matching row.
- **A resolution stack** for "resolve another card", which can nest and costs no Bot action (REQ-SOLO-100 to -102).
- **The Bot actions:**
  - gain and take, using the "A > B / C" precedence and the Junk rules (REQ-SOLO-140 to -149);
  - junk the card most valuable to the human;
  - promote, with the one-Duty-Officer limit and the SUITS flip (REQ-SOLO-91 to -95);
  - log, where a logged Incident is returned instead (REQ-SOLO-110);
  - deploy, keeping deployment order;
  - explore and engage;
  - send Away Teams to the Location with the most Bot tokens, never over-securing and never past more enemy Ships (REQ-SOLO-160 to -170);
  - take an Away Team from the Location with the fewest tokens when the Captain has none left;
  - Locations move to the Control Area after resolving.
- **Bot attacks** (REQ-SOLO-180 to -185):
  - the bold red parts run as an attack on the human, so the human's "when attacked" Reactions apply;
  - the human makes the choices those parts ask for;
  - a cancelled attack skips only the red parts.
- **Soval's rows**, from his command-card spec, including his special rule: Path of Surak cards are discarded instead of logged.
- **Acceptance test:** the solo rulebook's complete Bot turn (requirements/22-solo-mode.md §13), with every step checked.

**You test:** play against the Soval Bot at Admiral. The log names each card flipped, the row it matched and what happened. Check a few turns against the command card on screen.

## Step 3: Your cards against the Bot, SURPRISE operations, and Ticking Clock (done)

Making every human card behave correctly against a Bot opponent, through the hook from design decision 4:

- **Forced choices:** the Bot picks the first option it can legally resolve (REQ-SOLO-112, -113). For example, *Stone of Gol* makes it dismiss its Duty Officer.
- **Incidents:** the Bot declines any chance to return an Incident (REQ-SOLO-111, -187). Incidents given to it, or that it is forced to take, go on top of the Bot deck (REQ-SOLO-148).
- **Draws:** "draw a card" for the Bot discards the top card of the Bot deck instead (REQ-SOLO-186).
- **Resources:** the Bot gains them normally (REQ-SOLO-188). Steals succeed and come from the supply, never from the Bot (REQ-SOLO-195).
- **Attacks on the Bot's hand or Discard pile** (REQ-SOLO-190 to -194):
  - you choose whether the attack succeeded or failed;
  - when it did nothing, you may move the top Bot discard onto the Bot deck.
- **The Bot's Duty Officer and Ships:**
  - recalling its Duty Officer dismisses it instead;
  - a forced Ship dismissal takes its most recently deployed Ship;
  - a recalled or dismissed Ship goes to its Discard pile (REQ-SOLO-94, -165, -166).
- **SURPRISE operations:** *Dilithium Shockwave*, *Knowledge of a Terrible Fate* and *Time Is Running Out*.
- **Ticking Clock** (REQ-SOLO-130 to -133): *Time Is Running Out* goes into the Bot's Supplement deck when chosen.
- **Tests:**
  - a test per case above, using representative attack cards: *Stone of Gol*, *Malik*'s steal, *Ambassador Gral*, *Ash Tyler*, *Rumdar*'s forced discard and *Jackabog's Clumpship*;
  - random games against the Soval Bot with every Market card forced into the human's deck.

**You test:** play your attack cards against the Soval Bot and answer the "did it succeed?" prompt. Then start a game with Ticking Clock on.

## Step 4: The Georgiou, Kirk and Archer Bots (done)

Three Crews with no Bot special rule, except that Archer's row adds Away Teams from the supply, up to 6 (`ADD_AWAY_TEAM`). Each row is written from its spec, with the spec's Tests cases.

**You test:** one game against each of these Bots. Watch for the Kelpien row continuing to the SUITS card (Georgiou), and Archer's Bot gaining Away Teams.

## Step 5: The Pike, Riker, Freeman and Rebner Bots (done)

The four Crews with special rules:

- **Pike:** a resolved card with Skill icons raises the Bot's matching track; with several, the higher one.
- **Riker:** cards with NX-01, Android, Pakled, Lower Decker, Beverage or Betazoid are worth 1 more to the Bot.
- **Freeman:**
  - Lower Decker cards are discarded instead of logged when logging the top of the Bot deck;
  - Lower Decker cards are worth 1 more to the Bot;
  - his California-class fleet counts as 2 tokens for the Bot too (REQ-EXP-FRE-02).
- **Rebner:** Research and Influence are always ×0 for the Bot.

Then the strict check: the registry test requires a function for every row of every Bot except Khan's. Random games run against every Bot at every difficulty.

**You test:** one game against each of these Bots. With Pike, watch his tracks rise as he resolves cards with Skill icons.

## Step 6: Watching the Bot (done)

The client side of following a Bot turn:

- **Playback** of the Bot's turn from the log, one step at a time, with Next, Auto-play and Skip (REQ-SOLO-56):
  - the card being flipped is shown in the Staging Area;
  - the matched row is highlighted on the command card;
  - where it went is shown.
- **Prompts during the Bot's turn:** the attack choices and "did your attack succeed?" get clear wording, and the can't-be-undone warning where they are final (REQ-SOLO-201).
- **Undo:** ending your turn against the Bot shows the warning, because the Bot's turn cannot be undone (REQ-SOLO-200).
- **The solo player aid** as an in-app reference (§15): the Bot turn flow, the value rules, and the term table.

**You test:** play a game using Next to step through each Bot turn, then switch to Auto-play. Open the player aid.

## Step 7: Five-Year Mission, the core campaign (done)

The campaign without bonuses and challenges:

- **Storage:**
  - a campaign record holding your Crew, campaign mode, rank, assignments, Reinforcement pile and active bonuses (REQ-CAMP-50 to -52);
  - it is reached by its own secret link (design decision 7).
- **Assignments:**
  - choose a Bot you haven't beaten in this campaign, or pick one at random;
  - the difficulty comes from the rank × mode table;
  - rank goes up on a win, and a tie is a failure (REQ-CAMP-01 to -10).
- **The Reinforcement pile and *Reinforce*** (REQ-CAMP-20 to -24):
  - *Reinforce* is shuffled into your starting deck when the pile has cards;
  - it takes a card from the pile with `TAKE_FROM_REINFORCEMENT`;
  - cards left in the pile at game end don't score.
- **Upgrades, option A only:** add a matching Market card you had during the game. This uses the beaten or failed Bot's WIN or LOSS restriction.
- **The end:** after 10 assignments, or on reaching Admiral, the campaign ends with the performance review (§14.5).
- **Client:** a campaign screen with the log, rank, Reinforcement pile and final review, and New Game starts the next assignment from it.

**You test:** start a campaign, play two assignments, pick an upgrade after each, and see the reinforced card come back through *Reinforce* in the next game.

**What was done:** `engine/campaign.py` holds the rules (ranks, the difficulty table, upgrade restrictions, option A cards, the review). `app/routes/campaigns.py` stores the campaign (`Campaign` model, `X-Campaign-Token`) and records each result when its game is over; a deleted game counts as a failure. Each assignment is an ordinary solo game whose `campaign` column carries the Reinforcement pile; *Reinforce* (2DIR02) is card code. The client has New Five-Year Mission (from the Lobby), the campaign page, which starts each assignment itself rather than through New Game, a "Your Five-Year Missions" list in the Lobby, and a link back from the game. With no option A card the upgrade is skipped until option B arrives in Step 8.

## Step 8: Campaign bonuses and challenges (done)

- **Option B bonuses:** every Bot's WIN and LOSS bonuses, written as code (CLAUDE.md "Card effects are code" covers campaign upgrade bonuses).
  - REINFORCE bonuses move one of your own cards to the Reinforcement pile.
  - BOOST bonuses run at their stated moment in every later game: before or after drawing the starting hand, or at the start.
- **The seven challenges** (REQ-CAMP-40, -41):
  - *Live Long and Prosper*;
  - *That Is Not a Weakness; That Is Life*;
  - *Two Weeks to the Closest Outpost*;
  - *Running Like a Baby Gazelle*;
  - *Rules of Acquisition*;
  - *Only Ship in the Quadrant*, which ends the game at once as a failure;
  - *They Will Arrive on Tuesday*.

  Each is enforced by the engine, and challenges that don't fit your Crew are hidden.
- **Tests:** each bonus and challenge.

**You test:** a campaign with two challenges on. Pick an option B bonus after an assignment and check it applies in the next game.

**What was done:** every Bot's option B bonuses except Khan's are code in `engine/upgrades/<crew>.py`: 27 Boosts and 5 REINFORCE bonuses. Boosts run in a new `setup` step around the starting hand. The seven challenges are in `engine/campaign.py` (`game_setup`, `available_challenges`, `option_b`) and in setup or the engine (Only Ship, Tuesday). The campaign page offers options A and B, REINFORCE card picks, the Live Long resource choice, and the challenges, Boosts and next-game notes. The new-campaign page lists only the challenges the chosen crew can take, and the game mat shows the Reinforcement pile, Boosts, set-aside Away Teams and Only Ship. Rulings are in `resources/scans/OPEN_QUESTIONS.md`. REQ-CAMP-27's Pike example was corrected to match the printed card.

## Step 9: Final sweep (done)

- The solo acceptance scenario (§13) and every command-card spec test pass, plus random games against each Bot at each difficulty.
- An undo check: nothing in a Bot turn can be undone, and your own turn still can.
- CLAUDE.md: the Bot runtime, the `@row` decorator, the Bot actions, and how human actions behave against a Bot.
- Requirements updates: REQ-SRV-17 (design decision 1) and REQ-SRV-19 (solo games are no longer rejected).
- `scripts/card_coverage.py` reports Bot rows and campaign bonuses alongside cards.

**What was done:** `tests/test_solo_sweep.py` covers random games against all 8 available Bots at all 5 difficulties (Ticking Clock on every third), 6 random campaign games with all seven challenges, random Boosts and a Reinforcement pile, and an API check that your own moves can be undone but nothing across the Bot's turn can. REQ-SRV-17 and REQ-SRV-19 already described the in-engine Bot and solo games. `scripts/card_coverage.py` now has a group per Bot Crew and one for the bonuses: everything has code except Khan's rows, bonuses and SURPRISE cards, which wait with his deck.

## Not in this plan

- **The Khan Bot** and Khan's SURPRISE cards. They wait for Khan's open questions, like his deck.
- **The Core Box Burnham Bot** (REQ-SOLO-59, -72). Its content isn't in the app.
- **Using *Conspiracy* as a second Ticking Clock** (REQ-SOLO-132). It is a Core Box card, also not in the app.

## Rulings to confirm before Step 2

The command-card specs already settle most readings. These are noted there as "verify", with the reading the code will use:

- **Soval:** "Take [Research] / [Influence] / [Military]" means taking the most valuable card with any of those Skill icons, as in the rulebook's example where the Bot takes *Vidiians*.
- **Pike:** the Directive row with a Duty Officer lists six icons. It is read as gaining a card with any one of them.
- **Rebner:** the "[Military Focus]" icons on his rows are Focus icons, as printed with a folded corner.
- **Georgiou:** "You remove [Away Team]" names no Location, so you pick which of your Away Teams to remove.
