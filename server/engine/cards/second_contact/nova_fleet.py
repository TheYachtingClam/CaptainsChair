"""3ALL03 Nova Fleet (Ally). Spec: resources/scans/second_contact/cards/ally/3ALL03.md
The SUPPORT arrives in Step 7."""

from engine.cards import operation
from engine.ops import A


@operation("3ALL03", 0, uses=[A.GAIN_CARD, A.LOG])
def salvage(ctx, actions):
    """PLAY: Gain an Ally/Cargo from the Junk. Log this card."""
    yield from actions.gain_card(["Ally", "Cargo"], label="an Ally or Cargo from the Junk", only_junk=True)
    yield from actions.log(ctx.this_card)
