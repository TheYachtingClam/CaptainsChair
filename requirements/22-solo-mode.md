# 22 – Solo Mode: Starfleet Command Training Program (Playing Against the Bot)

Source: Solo rulebook, [resources/scans/to_boldly_go/solo/](../resources/scans/to_boldly_go/solo/). Page numbers in this file refer to the solo rulebook.

In solo mode, one human player plays against an automated opponent called **the Bot**. The Bot ignores the text on its cards. It acts using its **Automated Command cards**, based on the suit and traits of each card it resolves.

- **REQ-SOLO-01** The core rules apply in every situation unless this file says otherwise.
- **REQ-SOLO-02** The server runs the Bot. Every Bot decision follows the fixed rules below, so the Bot needs no AI and is fully deterministic apart from shuffles.
- **REQ-SOLO-03** The human wins by having **more** VP than the Bot after a Resolution. A tie is a loss. If the Burn happens, the human **loses**.
- **REQ-SOLO-04** The lobby should suggest Cadet Training ([16-solo-and-cadet-training.md](16-solo-and-cadet-training.md)) to first-time players, since solo mode has extra rules.
- **REQ-SOLO-05** Every Bot step is shown in the action log in plain words, including which Automated Command row matched and why, so the player can follow and check the Bot.

## 1. Difficulty

- **REQ-SOLO-10** Five difficulty levels, easiest to hardest: **Ensign, Lieutenant, Commander, Captain, Admiral**.
- **REQ-SOLO-11** Each level has its own Stardate cards, marked "Solo vs [difficulty] Bot". Each Stardate card shows the number of **Bot actions** for that stage of the game.

## 2. Setup (pp. 1–2)

1. **REQ-SOLO-20** The player chooses a difficulty level.
2. **REQ-SOLO-21** Perform the full central setup, with these changes:
   - Use the Stardate cards for the chosen difficulty.
   - The Bot gets no Action tokens and no Mission Completion tokens.
   - The human takes the Starting Player token and goes first.
3. **REQ-SOLO-22** Perform the human's player setup as normal.
4. **REQ-SOLO-23** Return the solo Directive cards *Reinforce* and *Time Is Running Out* to the box. They are used only by the Five-Year Mission campaign (§12) and the Ticking Clock challenge (§10).
5. **REQ-SOLO-24** Place the Bot's Crew board with the **Basic** side up, with all 3 Specialty markers at zero.
6. **REQ-SOLO-25** Split the Bot's Crew deck by position indicator. Shuffle any card marked Incident Deck into the common Incident deck.
7. **REQ-SOLO-26** Place the Bot's Captain card. Return any Status card from the Bot's deck to the box.
8. **REQ-SOLO-27 Supplement deck.** Shuffle all the Bot's **Development** cards into a facedown deck. Then shuffle all its **Reserve** cards and put them facedown on top. The combined pile is the Bot's **Supplement deck**.
9. **REQ-SOLO-28 Bot deck.** Shuffle all **Available** cards facedown. This is the **Bot deck**. If the Bot has any **Deployed** or **Controlled Location** cards, shuffle them together and put them facedown on top of the Bot deck.
10. **REQ-SOLO-29** Put any **Discard** cards faceup as the Bot Discard pile.
11. **REQ-SOLO-30** The Bot has two areas: a **Control Area** for its Duty Officer, Locations and deployed Ships, and a **Staging Area** for cards being resolved.
12. **REQ-SOLO-31** Put the number of Away Teams shown on the Bot's Captain onto it.
13. **REQ-SOLO-32** Find the Bot Crew's two Automated Command cards. Place them with the **"TRAITS"** side and the **"SUITS WITH NO DUTY OFFICER"** side face up.
- **REQ-SOLO-33** The Bot starts with **no resources**, not even Glory.
- **REQ-SOLO-34** The Bot has no hand. It never uses its Crew board's missions.

## 3. Value of cards (p. 3)

The Bot often chooses the "most valuable" or "least valuable" card. A card's value is how many VP it would score for the Bot if the game ended just after gaining it.

- **REQ-SOLO-40** A card's value to the Bot is the sum of:
  - its printed VP;
  - for each Focus icon, the Bot's current multiplier on that Specialty track;
  - **5** if it has an ENDGAME operation;
  - **1** per Glory token on the card. Other resources on the card do not count.
- **REQ-SOLO-41 Tie-breaks.** Among cards of equal value, the one with **more** resource tokens of any type is more valuable. If still tied, the Bot picks the **leftmost** card in the Market or Neutral Zone. The leftmost rule applies whether the Bot wants the most or the least valuable card.
- **REQ-SOLO-42 Value to you.** Some rules use a card's value **to the human**. This uses the same formula but with the **human's** current Specialty multipliers.
  - "Least valuable to you" picks the lowest value. It is used for Glory placement in the Bot's Clean-up.
  - "Most valuable to you" picks the highest value. It is used when the Bot junks a card.
- **REQ-SOLO-43** The engine exposes one value function with parameters for whose multipliers to use and the direction, so all Bot choices share one tested implementation.

## 4. Flow of the game (p. 4)

The human plays as normal. The Bot resolves each step as follows.

### Resupply Step

- **REQ-SOLO-50** The Bot has no Resupply Step.

### Control Step

- **REQ-SOLO-51** If the Bot has secured a Location, it takes control of it. If it has secured more than one, it takes the most valuable. Tokens there are dismissed or removed as usual, which can give the human Glory. Refill the Neutral Zone as usual.
- **REQ-SOLO-52** Place the Location in the Bot's Control Area, then resolve it using the Automated Command cards (§5). It stays in the Control Area unless a row tells the Bot to log it.

### Action Step

- **REQ-SOLO-53** Draw as many cards from the Bot deck as the **Bot actions** shown on the current Stardate card. This may cause a reshuffle. Place them facedown in a row in the Bot's Staging Area.
- **REQ-SOLO-54** Flip the first card face up and resolve it with the Automated Command cards. Repeat one card at a time until every card is face up and resolved.
- **REQ-SOLO-55** If an effect makes the Bot resolve another card (§7), resolve that card fully, then return to the card that triggered it.
- **REQ-SOLO-56** The client animates each Bot card being flipped and resolved, with a short pause or a "next" button, so the player can follow it.

### Clean-up Step

1. **REQ-SOLO-57** If the Bot has a Stardate card in its Staging Area, because the human emptied it last turn, perform its effect (such as wiping), then remove it from play.
2. **REQ-SOLO-58** Discard every card left in the Bot's Staging Area.
3. **REQ-SOLO-59** Choose the Market card **least valuable to the human**. On a tie, pick the one with **fewer** resource tokens, then the leftmost. Place 1 Glory on it, from the Stardate card or from the supply after a Resolution.
   - Core Box Burnham Bot: instead remove 1 Glory from the Stardate card and place 2 Dilithium from the supply on the chosen card.

### Reshuffling the Bot deck

- **REQ-SOLO-60** When the Bot deck is empty and the Bot needs it (to draw, discard or even look at a card), shuffle the Bot Discard pile, but **not** its Staging Area, into a new Bot deck.
- **REQ-SOLO-61** Then put the top card of the Supplement deck on top of the new Bot deck, and continue.
- **REQ-SOLO-62** This mirrors enlisting, but the Bot does not distinguish Reserve and Development cards, and never pays development costs.

## 5. Ending the game and scoring (pp. 4–5)

- **REQ-SOLO-70** If the game ends with the Burn, the Bot wins, no matter how many Incidents either side has.
- **REQ-SOLO-71** When a Resolution is triggered (the 5th Stardate card empties), finish the current round and play one more round. The game always ends with a Bot turn.
- **REQ-SOLO-72** Score both sides as in the core rules, with these changes for the Bot:
  - The Bot scores **5 VP for each ENDGAME operation it owns**, instead of evaluating it, whether or not the card is in play. This includes an ENDGAME on its Captain.
  - The Bot ignores its missions, but still scores its Specialty tracks and Focus icons.
  - Like the human, the Bot scores 1 VP per Glory and 1 VP per Bot token in the Neutral Zone, and its printed VP normally.
  - The Bot scores **1 VP for every 2** Dilithium and Latinum it has collected, combined.
  - Core Box Burnham Bot scores 1 VP for **each** Dilithium instead.
  - If a card the Bot owns has an **asterisk** VP, its SPECIAL operation **does** apply to the Bot. This happens outside play, so it is not an exception to the Bot ignoring card text.
- **REQ-SOLO-73** The human wins only with **more** points than the Bot.

## 6. Resolving Bot effects: Automated Command cards (pp. 5–6)

- **REQ-SOLO-80** The Bot **ignores all text on all its cards during play**. The only exception is SURPRISE (§6.2).
- **REQ-SOLO-81** Each Bot Crew has two Automated Command cards:
  - **TRAITS**: rows keyed by trait, in priority order. The top of the card may show a **special rule** for this Bot and a **SURPRISE** reminder row.
  - **SUITS**: rows keyed by suit. It is double-sided: **WITH NO DUTY OFFICER** and **WITH DUTY OFFICER**.
- **REQ-SOLO-82 Resolving a card:**
  1. Check the TRAITS card from top to bottom for the first trait the resolved card has. If found, stop looking.
     - A card with the **Wildcard** trait matches the **first trait row**, ignoring the SURPRISE reminder row.
  2. If no trait row matches, use the row on the SUITS card, on whichever side is face up, that matches the card's suit.
  3. Perform the matched row's effect, whatever the card's printed text says.
- **REQ-SOLO-83** Automated Command rows must be stored as structured data: a trait list or suit, plus an effect script, like card operations ([12-component-anatomy.md](12-component-anatomy.md)).

### 6.1 Specialties

- **REQ-SOLO-84** The Bot gains Research, Influence and Military the same way the human does and moves its tracks.
- **REQ-SOLO-85** When told to raise the highest or lowest of several tracks and they tie, the Bot picks the topmost: **Research, then Influence, then Military**.

### 6.2 "This card" and the Surprise trait

- **REQ-SOLO-86** On an Automated Command row, "this card" always means the card being resolved that matched the row.
- **REQ-SOLO-87** A card with the **Surprise** trait also has a **SURPRISE (Bot only)** operation. When the Bot resolves such a card, it performs the SURPRISE operation written on the card and ignores any Automated Command match. This is the only time the Bot uses its own card text during play.
- **REQ-SOLO-88** Example: *Dilithium Shockwave* (Incident, Surprise): "SURPRISE (Bot only): Gain 1 Glory and discard the top card of the Bot deck. You gain 2 Dilithium. Return this card."

### 6.3 Locations

- **REQ-SOLO-89** Whether a Location is played from the Bot deck or taken under control, the Bot resolves its matching row. If it is still in the Staging Area afterwards, meaning it was not logged, move it to the Bot's Control Area. This applies whichever row matched.
- **REQ-SOLO-90** A Location with no matching trait row uses the **Location** row on the SUITS card, then goes to the Control Area.

### 6.4 Duty Officers

- **REQ-SOLO-91** When an effect promotes a Person to the Bot's Duty Officer, move it out of the Staging Area to the front of the Control Area next to the Captain. Then flip the SUITS card to **WITH DUTY OFFICER**.
- **REQ-SOLO-92** The Bot has a limit of **one** Duty Officer. If a new one is promoted, put the previous one in the Bot Discard pile.
- **REQ-SOLO-93** If any effect dismisses or logs the Bot's Duty Officer, flip the SUITS card back to **WITH NO DUTY OFFICER**, unless a new Duty Officer was promoted at the same time.
- **REQ-SOLO-94** If an effect would make the Bot recall its Duty Officer, dismiss it instead.
- **REQ-SOLO-95** The Duty Officer's identity and traits do not matter to the Bot. Having one only unlocks the stronger SUITS rows. Some of those rows dismiss or log the Duty Officer as a cost. The human can also dismiss it with an Attack.

### 6.5 Bot Discard pile

- **REQ-SOLO-96** When an effect resolves, promotes or logs a card of a given suit or trait from the Bot Discard pile, use the **topmost** matching card, meaning the most recently discarded.

## 7. Resolving other cards (p. 7)

- **REQ-SOLO-100** When an effect tells the Bot to resolve another card, such as the top of the Bot deck, the top of the Supplement deck or a card it just gained, put it faceup in the Bot's Staging Area and resolve its matching row at once.
- **REQ-SOLO-101** This does **not** count against the Bot's actions for the turn. Afterwards, return to the original card's resolution.
- **REQ-SOLO-102** The engine needs a resolution stack for Bot cards, since these can nest.

## 8. Incidents and unspecified choices (p. 7)

- **REQ-SOLO-110** If a Bot effect would make the Bot log an Incident, it returns the Incident to the Incident deck instead.
- **REQ-SOLO-111** If one of the human's card effects gives the Bot a choice to return an Incident, the Bot declines.
- **REQ-SOLO-112** For any other choice a human card effect forces on the Bot, it picks the **first listed option it can legally resolve**, even if that option does nothing.
- **REQ-SOLO-113** Example: the human plays *Stone of Gol* ("For each Duty Officer your opponent has in play, force them to either: dismiss it OR exhaust it and you gain 1 Glory"). The Bot picks the first option and dismisses its Duty Officer, then flips its SUITS card back.

## 9. Continue resolution (p. 7)

- **REQ-SOLO-120** Some effects on the TRAITS card or in SURPRISE operations say "continue resolution". Stop the current row, ignoring the rest of it. Then find the **next** matching row using the same rules, and perform it.
- **REQ-SOLO-121** For a Wildcard card whose first TRAITS row says continue resolution, go on to the second row, and so on.
- **REQ-SOLO-122** Example: Georgiou Bot resolves *Vulcan Science Academy*. After the Vulcan row, it continues to the next match, the Location row on the SUITS card. For *Vice Admiral Pasalk*, it continues to the Attack row, which may itself continue to the Person row.

## 10. Ticking Clock challenge (p. 7)

- **REQ-SOLO-130** An optional challenge for expert players. Add the solo Directive *Time Is Running Out* to the Bot's Reserve cards when building the Supplement deck.
- **REQ-SOLO-131** It has the Surprise trait, so its effects are on the card (§6.2).
- **REQ-SOLO-132** With Core Box content, the Core Box card *Conspiracy* can be used instead, or both together for a bigger challenge.
- **REQ-SOLO-133** The game-creation screen offers Ticking Clock as a checkbox for solo games.

## 11. Market and Neutral Zone (p. 8)

### 11.1 Gaining and taking cards

When an Automated Command row tells the Bot to gain a card with a Skill, Focus, trait or suit:

- **REQ-SOLO-140 "A > B".** If the Market has a card with A, gain the most valuable one. Otherwise gain the most valuable card with B.
- **REQ-SOLO-141 "A / B".** Gain the most valuable card with A or B or both.
- **REQ-SOLO-142 Precedence.** ">" is resolved before "/".
  - "A > B / C": gain A if possible, otherwise the most valuable of B or C.
  - "A / B > C": gain the most valuable of A or B if possible, otherwise C.
- **REQ-SOLO-143** "If able" means the Bot gains nothing when no card matches.
- **REQ-SOLO-144** The Bot never gains from the top of a Market deck unless told to. It always picks faceup cards.
- **REQ-SOLO-145 From the Junk.** When the Bot gains "from the Junk", treat every Junk card as if it were in the Market. On a value tie, take the one most recently placed in the Junk.
- **REQ-SOLO-146 Including the Junk.** Consider the Junk and the Market together. On a tie, prefer the Market card, otherwise the most recent Junk card.
- **REQ-SOLO-147 Gain vs take.** For the Bot, *gain* puts the card in the **Bot Discard pile**. *Take* puts it on **top of the Bot deck**.
  - Bot rows may *take* Market suits and may *gain* Encounters or Incidents. Both work the same except for where the card goes.
  - Exception: when an Automated Command row tells the Bot to *gain* an Incident, it goes in the Bot Discard pile.
- **REQ-SOLO-148** When a human effect gives the Bot a card or forces it to take one, usually an Incident, put it on top of the Bot deck.
- **REQ-SOLO-149** The Bot also gains any resources on a card it gains or takes, usually Glory.

### 11.2 Junking

- **REQ-SOLO-150** "Junk the most valuable card in the Market (ignoring any with tokens)" picks the card **most valuable to the human** and junks it. Like the human, the Bot cannot junk a card with tokens on it.

### 11.3 Gaining resources

- **REQ-SOLO-151** The Bot gains Glory like the human. Glory not from the Market comes from the Stardate card, or from the supply after a Resolution. If a Stardate card empties on the Bot's turn, follow the core rules; usually the card goes to the human's Staging Area and the next one is filled.
- **REQ-SOLO-152** The Bot gains Dilithium or Latinum only in two cases:
  - someone is playing Core Box Burnham, which can put Dilithium in the Market for the Bot to gain and score;
  - a human card effect explicitly gives the Bot resources, such as *Dilithium Shockwave*.

### 11.4 The Neutral Zone (p. 9)

- **REQ-SOLO-160** When the Bot picks a Location for its Ship or Away Team tokens, it decides by the **number of tokens** already there. Ties go to the most valuable Location.
- **REQ-SOLO-161 No overcontrol.** The Bot never moves tokens to a Location in its own Control Area. It never moves tokens to a neutral Location where it already has **more than enough** to secure it, meaning it never exceeds the securing requirement by more than one token.
  - Example: the Bot has 3 Away Teams on *Dozaria* and the human has 1, so *Dozaria* is secured. A Bot Away Team sent "to the Location with most tokens" still goes there, making 4. After that, 4-to-1 is more than enough, so the Bot will not warp a Ship there, even when engaging.
- **REQ-SOLO-162** "More than enough" means the Bot has **4 or more** tokens there **and 3 or more** more than the human, per the solo player aid. Count tokens using their weights (REQ-EXP-FRE-03).

### 11.5 Deploying and warping Ships (p. 9)

- **REQ-SOLO-163 Deploy.** Move the Ship card to the Bot's Control Area with its Ship token on it. Keep Ship cards in the order they were deployed.
- **REQ-SOLO-164** "Explores" or "engages" moves the Ship token to a Neutral Zone Location, like a warp.
  - **Exploring:** warp to the Location with the **fewest total** tokens, preferring ones with none.
  - **Engaging:** warp to the Location where the **human has the most** tokens.
  - Ties go to the most valuable Location.
- **REQ-SOLO-165** When the Bot is forced to recall or dismiss a deployed Ship, it discards it.
- **REQ-SOLO-166** When the Bot chooses which Ship to dismiss, for example from a human "force your opponent to dismiss a Ship" attack, it dismisses the **most recently deployed** one.

### 11.6 Sending Away Teams (p. 9)

- **REQ-SOLO-167** Sending a Bot Away Team moves a token from the Bot's Captain to a Neutral Zone Location.
- **REQ-SOLO-168** Like the human, the Bot cannot send to a Location where its opponent has more Ship tokens, unless the effect says otherwise. Those Locations are excluded.
- **REQ-SOLO-169** The Bot prefers the Location where **it** already has the **most** tokens. A trait preference in the effect takes priority over token count. Ties, including zero, go to the most valuable Location.
  - Example: "send an Away Team to a neutral Xindi / Tellarite > Location" sends to a Xindi or Tellarite Location first, even if the Bot has more tokens elsewhere. Among several Xindi or Tellarite Locations, it picks the one where it has most tokens.
- **REQ-SOLO-170** If the Captain has no Away Team left, or an effect says to remove one, the Bot takes one from the Location where it has the **fewest** tokens, ignoring the target. Ties go to the one **least valuable** to the Bot.

## 12. Directly interacting with the Bot (p. 10)

### 12.1 Bot attacks

- **REQ-SOLO-180** A Bot effect is an **attack** if its row harms the human, whether or not the resolved card has the Attack trait. Attack parts are printed **bold and red** on the Automated Command card. The data must mark these parts.
- **REQ-SOLO-181** The human must resolve the bold red parts. The rest of the row is from the Bot's point of view.
- **REQ-SOLO-182** The human's Reactions that trigger on being attacked fire on these effects.
- **REQ-SOLO-183** Choices about how a Bot attack hits the human, such as which Ship to dismiss, are made by the **human** unless stated otherwise.
- **REQ-SOLO-184** If the human cancels an attack, only the bold red part is cancelled, and all of it. The rest of the row still resolves. A cancelled attack still counts as having happened.
  - Example: a row removes all the human's Away Teams from a Location where the Bot has a Ship, then logs the resolved card. With *Riva* on duty, no Away Teams are removed but the card is still logged.
- **REQ-SOLO-185** Effects that affect the human without being attacks are printed **bold but not red**.

### 12.2 Helping the Bot

- **REQ-SOLO-186** If a human effect offers or forces the Bot to draw a card, discard the top card of the Bot deck instead.
- **REQ-SOLO-187** If a human effect lets the Bot return an Incident, it declines.
- **REQ-SOLO-188** If a human effect gives the Bot a resource, it gains it normally: Dilithium and Latinum from the supply, Glory from the Stardate card.

### 12.3 Attacking the Bot

- **REQ-SOLO-190** Attacks that target the Bot's hand, such as reveal or force a discard, do nothing, because the Bot has no hand. Attacks that force the Bot to find a card or choose from its own Discard pile also do nothing.
- **REQ-SOLO-191** For those attacks, the human **chooses** whether the attack succeeded or failed.
- **REQ-SOLO-192** This differs from an attack that makes the Bot pick between two negative effects. There the Bot picks the first option it legally can (REQ-SOLO-112).
- **REQ-SOLO-193** Whenever an attack does nothing for these reasons, the human **may** move the top card of the Bot Discard pile onto the top of the Bot deck. If the human chose to resolve it as a failed attack, they cannot do this.
  - Example 1: "Force your opponent to discard a card" is skipped. The human may move the top Bot discard to the top of the Bot deck. If the effect repeats, they may do it again.
  - Example 2: "Force your opponent to log a Person from hand or Discard pile. If they do, they draw a card. If they cannot, they take an Incident." The human chooses success (optionally moving a card, after which the Bot "draws" by discarding one) or failure (the Bot takes an Incident).
- **REQ-SOLO-194** The client shows the human a prompt for REQ-SOLO-191 and REQ-SOLO-193.
- **REQ-SOLO-195 Stealing.** Since the Bot usually has only Glory, any **steal** effect the human resolves, including stealing Glory, automatically succeeds. The resources come from the **supply**, never from the Bot. This does not count as gaining, so gain Reactions do not trigger, and stolen Glory does not come from the Stardate card. Even if the Bot has Dilithium or Latinum, the human cannot steal it.

## 13. Acceptance scenario: complete Bot turn (pp. 11–15)

The human plays against the Admiral Soval Bot. This is one automated test.

1. **Control Step.** Nothing happens; the Bot has not secured a Location.
2. **Action Step.** The Stardate card shows 4 Bot actions, so 4 cards are drawn facedown.
3. **Card 1: *Subcommander T'Pol*** (traits Telepath and Scientist). The Telepath row is higher on Soval's TRAITS card, so it matches.
   - The row offers the human the chance to return an Incident. The human does, so the Bot resolves the top card of the Bot deck: *Political Crisis*, an Incident.
   - *Political Crisis* uses the Incident row of SUITS WITH NO DUTY OFFICER: log the top card of the Bot deck, gain a Person, return this card.
   - The top card is *Infinite Diversity in Infinite Combinations*, which has Path of Surak. Soval's Bot special rule says such a card is discarded instead of logged.
   - The Bot gains a Person: *Hoshi Sato* goes to the Bot Discard pile and *Riva* is revealed in the Market. *Political Crisis* goes to the bottom of the Incident deck.
   - Back on T'Pol's Telepath row: T'Pol is a Person, so she is promoted. The SUITS card flips to WITH DUTY OFFICER.
   - "Continue resolution" then resolves the Scientist row: gain 1 Glory, and take a card with a Skill icon.
   - Candidates: *Riva* (1 Influence Skill), *Xindi-Aquatic Cruiser* (2 Influence Skills) and *Vidiians* (1 Research Skill). The Cruiser is worth 2. With Soval's Influence at 8, *Riva* is worth 4. *Vidiians* is also worth 4 because of a Glory token on it. The token breaks the tie, so the Bot takes *Vidiians* and its Glory. *Take* puts it on top of the Bot deck.
4. **Card 2: *Stel*** (Attack, Vulcan). The Attack row matches: "If Bot has 8 or fewer Military, you remove an Away Team from a neutral Location, if able, then send a Bot Away Team to the same Location, if able. If either option failed, gain 2 Military. If Bot has 9+ Military, take control of a neutral Location you have not secured, then log this card."
   - The Bot has 4 Military. The human chooses to remove an Away Team from *Delta Vega*.
   - The Bot cannot send an Away Team there, because the human has more Ships there. So the Bot gains 2 Military.
5. **Card 3: *Species 10-C***, an Encounter that could also count as an Ally for a human. The Bot ignores the printed operation and treats it as an Encounter. The Encounter row with Duty Officer: gain 1 Research, gain 1 Influence, resolve the top card of the Supplement deck, then log *Species 10-C*.
6. **Card 4: *Paan Mokar*** (Vulcan, Andorian). Neither trait is on the TRAITS card, so the Location row of SUITS WITH DUTY OFFICER is used: gain 1 Influence, gain a Research Focus > Starfleet > Cargo card, then log the Duty Officer.
   - No Market card has a Research Focus, so it gains *EVA Suit*, the only Starfleet card.
   - T'Pol is logged, and the SUITS card flips back to WITH NO DUTY OFFICER.
   - *Paan Mokar* moves to the Bot's Control Area under the Location rule.
   - The top card resolved from the Supplement deck is *Seleya*, which matches the Ship row: deploy it; it explores; gain 1 Military; send an Away Team to a neutral Location.
   - Exploring: *Delta Vega* has one human Ship and *Indri VIII* has one Bot token. They tie on token count, so value decides. *Indri VIII* is worth 5 and wins.
   - The Away Team goes to the Location where the Bot has the most tokens, *Indri VIII*, which secures it.
7. **Clean-up Step.** *Stel*, the only card left in the Staging Area, is discarded.
   - Glory placement: with the human's Influence multiplier at ×2, *Riva* is worth 2 to the human, tied with the printed 2 VP of both Xindi cards. None has tokens, so the leftmost, *Riva*, gets the Glory.
   - That empties the Stardate card. It goes to the human's Staging Area and will trigger in the human's next Clean-up. The next Stardate card is filled with 6 Glory.

## 14. Five-Year Mission: solo campaign (pp. 16–18)

A campaign is a series of solo games against different Bots, where the human earns promotions and upgrades their Crew deck between games.

### 14.1 Structure

- **REQ-CAMP-01** Each game is a six-month **assignment**. The campaign ends after **10 assignments**, or immediately when the human reaches the rank of **Admiral**.
- **REQ-CAMP-02** When starting a campaign, the human chooses their Crew deck and a **campaign mode**. Their starting rank is always **Ensign**.
- **REQ-CAMP-03** Campaign modes, easiest to hardest: **Set Phasers to Stun, Yellow Alert, Gates of Sto'Vo'Kor, The Kobayashi Maru**.
- **REQ-CAMP-04** For each assignment, the human chooses a Bot opponent or has one picked at random. They may use either side of their Crew board.
- **REQ-CAMP-05** The human **cannot** choose an opponent they have already beaten in this campaign.
- **REQ-CAMP-06** A tie against the Bot counts as a failure.
- **REQ-CAMP-07 Promotion.** Each success raises the human's rank: Ensign, Lieutenant, Commander, Captain, Commodore, Admiral. Reaching Admiral means five victories and ends the campaign as a win.
- **REQ-CAMP-08** Whether the human succeeds or fails, they choose one upgrade after each assignment (§14.3).

### 14.2 Bot difficulty

The Bot's difficulty depends on the human's current rank and the campaign mode.

| Human rank | Set Phasers to Stun | Yellow Alert | Gates of Sto'Vo'Kor | The Kobayashi Maru |
|---|---|---|---|---|
| Ensign | Ensign | Lieutenant | Commander | Admiral |
| Lieutenant | Lieutenant | Commander | Captain | Admiral |
| Commander | Commander | Captain | Admiral | Admiral |
| Captain | Captain | Captain | Admiral | Admiral |
| Commodore | Captain | Admiral | Admiral | Admiral |

- **REQ-CAMP-10** The server sets the Bot's difficulty from this table. The player cannot change it within a campaign.

### 14.3 Reinforcement pile and upgrades

- **REQ-CAMP-20 Reinforcement pile.** A campaign-only zone of cards the human has earned. It carries over to every later game in the campaign, even if that game uses common cards from a different set.
- **REQ-CAMP-21** If the Reinforcement pile has at least one card, shuffle the solo Directive ***Reinforce*** ("Solo Campaign Only") into the human's starting deck. *Reinforce* has two PLAY operations: take a card from the Reinforcement pile; or, if the pile is empty, draw a card; then log *Reinforce*.
- **REQ-CAMP-22** Reinforcing is separate from enlisting Reserves and Developments.
- **REQ-CAMP-23** Cards left in the Reinforcement pile at game end do **not** score. A card only counts as owned once taken with *Reinforce*.
- **REQ-CAMP-24 Prohibition.** An Encounter, an Incident, or a common Location can never be added to the Reinforcement pile.
- **REQ-CAMP-25 Upgrade options** after each assignment. The human picks one:
  - **Option A.** Add a Market card the human had during the game that matches the restriction of the opponent just faced to the Reinforcement pile. If they have no matching card, they must choose option B.
  - **Option B.** Choose one alternative bonus for the opponent just faced.
- **REQ-CAMP-26** Each Bot Crew has a **"FIVE YEAR MISSION: UPGRADES"** Automated Command card. It has a **WIN** section and a **LOSS** section. Each lists:
  - A: the common card types the human may reinforce;
  - B: the alternative bonuses to pick from.
- **REQ-CAMP-27** Example, Pike's upgrade card:
  - WIN. A: Time Travel or Doctor. B: "BOOST: Before drawing the starting hand, take an Incident to enlist a Development" or "BOOST: Gain 1 Research, 1 Influence, and 1 Military."
  - LOSS. A: Ship. B: "REINFORCE: A card with Research, Influence or Military from your Available cards or Reserve deck" or "BOOST: After drawing the starting hand, free play a non-Time Travel card, then recall it."
- **REQ-CAMP-28** Example, Kirk's upgrade card: WIN lets the human reinforce any Person. LOSS allows a Market card of any suit with Vulcan, Time Travel or Klingon. LOSS bonuses include moving a non-Incident card from the human's own Reserve deck to the Reinforcement pile. WIN bonuses are Boosts: "gain 2 Research or 2 Influence or 2 Military", or "send an Away Team each to two different neutral Locations".
- **REQ-CAMP-29 Reinforce bonuses** add one of the human's own cards to the Reinforcement pile. It starts there in every later game.
- **REQ-CAMP-30 Boost bonuses** resolve at the start of every later game in the campaign, at the moment the bonus states.
- **REQ-CAMP-31** Upgrade cards and their options are stored as structured data, like Automated Command rows.

### 14.4 Challenges

The human may add any of these optional challenges when starting a campaign, at any campaign mode:

| Challenge | Rule |
|---|---|
| Live Long and Prosper | After a success, start the next game with no Dilithium **or** no Latinum, the player's choice. After another success, start with neither. This continues until a failure, which resets starting resources to normal. |
| That Is Not a Weakness; That Is Life | At rank Lieutenant or higher, during setup: note the size of the Reserve deck, shuffle the Reserve and Available cards together, deal a new Reserve deck of the same size at random, and use the rest as the starting Draw deck. |
| Two Weeks to the Closest Outpost | After a success, shuffle *Reinforce* into the Reserve deck for the next game instead of the starting Draw deck. After a failure, it goes back in the starting deck. |
| Running Like a Baby Gazelle | After two successes in a row, shuffle one Incident from the Incident deck into the starting Draw deck. Repeat each game, at most one Incident, until a failure. |
| Rules of Acquisition | After a success, upgrade option B is not available. If the human owns no matching card, they get no upgrade. |
| Only Ship in the Quadrant | If the human's starting Ship is ever dismissed or recalled, they fail the assignment. Not available for Crew decks without a starting deployed Ship. |
| They Will Arrive on Tuesday | Set one Away Team aside at setup. It returns to the Captain when the Reserve deck empties. After a success, set **two** aside in the next game, returned the same way. Not available for Crew decks without a Reserve deck. |

- **REQ-CAMP-40** The engine enforces every chosen challenge automatically. *Only Ship in the Quadrant* ends the game at once as a failure.
- **REQ-CAMP-41** The campaign setup screen hides challenges that are not available for the chosen Crew deck.

### 14.5 Performance review

At the end of the campaign, show the evaluation for the final rank:

| Final rank | Evaluation |
|---|---|
| Ensign | You are like an eternal Harry Kim. |
| Lieutenant | You are like Picard, but in a blue shirt. |
| Commander | You are far from the bones of your ancestors. |
| Captain | The *California*-class needs captains, too… |
| Commodore | You'll be leading a backwater sector… |
| Admiral, in 9–10 assignments | Welcome to Starfleet Command! |
| Admiral, in 7–8 assignments | Section 31 will be in touch… |
| Admiral, in 5–6 assignments | The Legends: Archer, Kirk, Picard, you… |

### 14.6 Campaign log

- **REQ-CAMP-50** The server stores each campaign as a record replacing the paper logbook: the human's Captain, campaign mode, chosen challenges, and one row per assignment.
- **REQ-CAMP-51** Each assignment row records the date, the human's rank, the Bot's Captain, the Bot's difficulty, both scores, and the upgrade chosen.
- **REQ-CAMP-52** The campaign record also holds the current Reinforcement pile and active Boosts. New games in the campaign are set up from it automatically.
- **REQ-CAMP-53** The client shows a campaign screen with the log, current rank, Reinforcement pile, Boosts and final rank.
- **REQ-CAMP-54** Campaigns belong to a seat token or a named player profile on this server, so a player can continue across sessions. Players do not have accounts (see [19-technical-architecture.md](19-technical-architecture.md)).

## 15. Solo player aid (in-app reference)

The in-app reference for solo games includes the solo player aid: the Bot turn flow, the value rules, and these common Bot terms.

| Term | Bot meaning |
|---|---|
| Gain | Card to the Bot Discard pile. From the Market, prefer the most valuable |
| Take | Card to the top of the Bot deck. From the Market, prefer the most valuable |
| Deploy | Move to the Control Area, keeping deployment order |
| Dismiss, Discard, Recall | Card to the Bot Discard pile. If the Duty Officer went, flip the SUITS card. When choosing a Ship, pick the most recently deployed |
| Promote | Move the Person to the Control Area. Flip SUITS if there was no previous Duty Officer |
| Log | Move under the Captain. If the Duty Officer was logged, flip SUITS |
| Explore | Warp to the neutral Location with the fewest total tokens. Ties: most valuable |
| Engage | Warp to the neutral Location with the most human tokens. Ties: most valuable |
| Send Away Team | To the neutral Location with the most Bot tokens. Ties: most valuable. Excludes Locations where the human has more Ships |
| Junk | The Market card most valuable to the human, excluding cards with resource tokens |
| Continue resolution | Stop the current row and resolve the next matching row |

## 16. Undo in solo games

- **REQ-SOLO-200** Undo works as in [20-undo.md](20-undo.md). The Bot's whole turn is a sequence of irreversible events, because it draws and reveals cards. Ending the human's turn therefore shows the usual warning, and nothing in the Bot's turn can be undone.
- **REQ-SOLO-201** Choices the human makes during the Bot's turn, such as which Away Team to remove or whether an attack against the Bot succeeded, show the can't-be-undone warning when they are final.
