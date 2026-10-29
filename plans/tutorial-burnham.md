# Plan: "Burnham" (short)

Burnham is complexity 7 of 10, but nearly all of it is one rule, *Inert Dilithium* ([requirements/23-core-box.md](../requirements/23-core-box.md) §4.1, REQ-CORE-30 to -34). A short tutorial is enough. See [tutorials-roadmap.md](tutorials-roadmap.md).

## What the player should know at the end

- **Inert Dilithium**, her Status card, is in play from the start. While it is:
  - Dilithium she gains goes onto the card, not into her supply (but not the Dilithium on a Market card she gains);
  - Dilithium on the card can't be spent and isn't counted as hers;
  - her hand size is 1 higher;
  - she can't spend Glory as Dilithium.
- **Recrystallize** moves Dilithium from the card to her supply. It is not gaining, so nothing that triggers on gains triggers.
- **Her Clean-up:** instead of placing 1 Glory, she removes 1 Glory from the Stardate card and puts 2 Dilithium on a Market card.
- **Stealing:** an opponent steals from the card first. Dilithium she steals goes to her supply, because stealing is not gaining.
- **Theta Zeta** recrystallizes everything and logs Inert Dilithium, ending the rule.
- **U.S.S. Discovery-A**, her deployed Ship: its Dilithium can't be stolen.

## Decisions

1. **Cadet Training, 2 guided turns** (about 25 steps). Stacked to show:
   - a gain going onto the card;
   - a turn where she can't afford something even though she "has" Dilithium;
   - a recrystallize;
   - her Clean-up.
2. **Stealing and Theta Zeta are tips.** Cadet Training has no opponent who steals, so stealing is a tip that points to the Bot game.
3. **Assumes the Picard tutorial.**

## Steps

1. ✅ **Script** (for your review; `server/content/tutorials/burnham-basics.yaml`, 33 steps).
2. ✅ **Framework:** none needed. The coach's `show` needs a target for the Dilithium on Inert Dilithium.
3. **Check** on phone and laptop.
4. **Deploy** on your word.
