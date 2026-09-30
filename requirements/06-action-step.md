# 06 – Turn Step 3: Action Step

Source: Rulebook pp. 10–11.

## 1. Actions and operations

- **REQ-AS-01** Most gameplay is resolving card **operations**. The most common are **PLAY** and **ACTIVATION**.
- **REQ-AS-02** There is no limit on operations per turn. A player has **3 actions** per turn.
- **REQ-AS-03 Action cost.** An operation that starts with the action icon (a pen/stylus symbol) costs one action.
  - Spending an action flips one Action token to its spent side and places it on the card as a reminder.
  - If no Action token is available, the operation cannot be resolved.
- **REQ-AS-04 Optional vs mandatory.** All effects of a resolved operation are mandatory unless preceded by "may".
  - If a **cost** cannot be paid, the operation cannot be resolved.
  - If a non-cost effect cannot be resolved (a useless benefit), skip it.
  - A cost is spending resources, or any effect "A" in a "do A to do B" sentence.
- **REQ-AS-05 Attack operations.** An operation preceded by **ATTACK** negatively affects the opponent.
  - If an Attack forces the opponent to choose an effect, they must choose one they can fully resolve.
  - "ATTACK" does not change whether the operation costs an action.

## 2. Play operations

- **REQ-AS-10** During the Action Step a player may play any number of cards from hand.
- **REQ-AS-11** To play a card, move it to the Staging Area and resolve exactly **one** of its PLAY operations fully. PLAY operations are shown on a white background.
- **REQ-AS-12** If none of its PLAY operations can be resolved, the card cannot be played.
- **REQ-AS-13** After resolving, the card **stays** in the Staging Area unless an effect moves it (deploy, log, promote, etc.). Its traits and suit still count for the rest of the turn, for example toward mission goals.
- **REQ-AS-14 Cannot be played.** Some cards say "THIS CARD CANNOT BE PLAYED". They cannot move from hand to the Staging Area, but can still be beamed, discarded, promoted, etc.

## 3. Table operations

Table operations are usable on cards **in play but not in the Staging Area and not beamed**: a deployed Ship, a deployed Ongoing, a controlled Location, or a Person in the Duty Officer slot.

- **REQ-AS-20 ACTIVATION.**
  - Usable at any time during the owner's Action Step: before, after or between card plays, but never in the middle of another operation.
  - Exhaust the card first, then resolve.
  - An exhausted card's Activation cannot be used until refreshed.
  - If a card has several Activations, choose one.
- **REQ-AS-21 PASSIVE.** Passives work only while the card is in a table position: Fleet Area, Location Area, Duty Officer slot, or as the Captain or Status card. They never work from the Staging Area or while beamed. This includes "this card has" Passives, such as extra Skill icons.
  - Always in effect, on either player's turn, even while the card is exhausted.
  - Condition-triggered Passives may fire any number of times.
  - Passives are mandatory even when not beneficial.
- **REQ-AS-22 REACTION.** Reactions follow the same position rule as Passives (REQ-AS-21): they work only from a table position, never from the Staging Area or while beamed. A card deployed or taken under control by its own operation is in a table position and may react at once (KW-REA-03).
  - May be used whenever its trigger condition is met, including outside the Action Step and on the opponent's turn.
  - Exhaust the card first, then resolve.
  - Cannot be used while the card is exhausted.
  - The UI must prompt the owner when a Reaction becomes available, including on the opponent's turn. See [14-keywords.md](14-keywords.md).
- **REQ-AS-23 Exhaust / refresh.** Exhausted cards are shown rotated sideways. Refreshing rotates them back.
- **REQ-AS-24 Promoting.** A Person's table operation works only while the Person is a **Duty Officer**. Playing the Person to the Staging Area is not enough. A specific ability, usually on the starting Ship, promotes a Person.
- **REQ-AS-25 Not on the table.** Table operations of cards in the Staging Area (an unpromoted Person, an undeployed Ship) or of beamed cards cannot be resolved.

## 4. Completing goals (missions)

- **REQ-AS-30** During the Action Step the player may complete one or more missions whose **GOAL** is currently met.
  - Immediately resolve the **REWARD**.
  - Mark the mission with a Mission Completion token.
- **REQ-AS-31** If a **beamed** card contributes to completing a mission, that beamed card is dismissed. Other contributing cards are not. See [09-ships-locations-away-teams-beaming.md](09-ships-locations-away-teams-beaming.md).
- Mission details are in [10-missions-and-specialties.md](10-missions-and-specialties.md).

## 5. Unused actions

- **REQ-AS-40** Unused actions are lost at the end of the turn. Some **CLEAN-UP** operations reward unused actions.

## 6. Operation types on a card (reference)

| Operation | When used |
|---|---|
| PLAY (may have an action cost) | When played from hand |
| ACTIVATION / PASSIVE / REACTION (table operations) | While in the table position |
| CONTROL | When the Location is taken under control |
| RESUPPLY | Resupply Step |
| CLEAN-UP | Clean-up Step |
| ENDGAME | Final scoring |
| SPECIAL | As stated on the card |
| SUPPORT (expansion) | From hand, when its trigger happens in the owner's Action Step. See [21-expansion-second-contact.md](21-expansion-second-contact.md) |
| SURPRISE (Bot only) | When the Bot resolves the card. See [22-solo-mode.md](22-solo-mode.md) |
