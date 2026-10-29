# Plan: "Khan"

Khan is complexity 9 of 10: his deck replaces core rules ([requirements/15-crew-decks.md](../requirements/15-crew-decks.md) §4, rulebook p. 35). See [tutorials-roadmap.md](tutorials-roadmap.md).

## What the player should know at the end

- **The trait board instead of Specialty tracks.**
  - After every gain, and before the CONTROL of a Location you take, you may mark one trait of that card.
  - Taking a card (an Encounter or Incident) never marks.
  - A Wildcard counts as any trait for marking.
  - The last two slots depend on the opponent's Captain; in Cadet Training, on a random other Captain.
- **No tracks.**
  - "Gain 1 Research" does nothing for him.
  - Specialty requirements and Focus icons work differently until he is Wrathful.
- **His hand size**, and why it changes when his Captain flips.
- **No Reserve:** reshuffles enlist nothing. His Developments come through *Devastated Ceti Alpha V*.
- **Double-sided cards.**
  - Ceti Alpha V turns into Devastated Ceti Alpha V.
  - His Captain becomes Wrathful Khan through the mission *I Shall Leave You as You Left Me*: Focus scores, and Specialty requirements are all met.
- **Incidents as a resource:** his own Incidents, giving them, and managing the Burn.

## Decisions

1. **Cadet Training**, like the Picard tutorial: no opponent's turns to follow. The rival Captain for the two opponent slots is stacked (F2) and named on screen, so the coach can explain those two slots by name.
2. **3 guided turns**, stacked so they show:
   - marking after a gain;
   - marking before a CONTROL;
   - the Wildcard;
   - a "gain Research" that does nothing;
   - a reshuffle with no Reserve.
   Ceti Alpha V's flip goes in the guided turns if the stacked deck can reach it in three turns; otherwise it becomes a tip.
3. **Becoming Wrathful is a tip**, not a guided step: it comes too late in a game to script.
4. **Assumes the Picard tutorial:** it skips the general turn and explains only what Khan changes. The lobby recommends Picard first.

## Steps

1. **Script** (for your review). Play the stacked game through, then write the steps, More texts and tips:
   - the first opponent-slot mark;
   - Devastated Ceti Alpha V;
   - the mission's goal;
   - becoming Wrathful;
   - final scoring with marked traits.
2. **Framework:**
   - F2: the rival Captain, and the Development order if a step uses it;
   - F4: an `expect` form for a mark, written from the engine's option ids;
   - F5: the lobby's Captains group, and the link on the New Game screen;
   - the coach's `show` targets for the trait board's slots.
3. **Check** on phone and laptop. The trait board is small on a phone, so the slot highlights get their own look.
4. **Deploy** on your word.
