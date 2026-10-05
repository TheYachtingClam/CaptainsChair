"""2ALL09 Orion Syndicate (Ally). Spec: resources/scans/to_boldly_go/cards/ally/2ALL09.md
The first PLAY steals (an attack) and arrives in Step 4."""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import count_traits, has_trait


@operation("2ALL09", 1, uses=[A.GAIN_ACTION, A.DRAW, A.LOG],
           cost=[DiscardFromHand(1, lambda ctx, i: has_trait(i, "Shady"), "a Shady")])
def syndicate_favour(ctx, actions):
    """PLAY: Discard a Shady to gain an [Action]. If you have another Orion in play, draw 2 cards. Log this card."""
    yield from actions.gain_action(1)
    if count_traits(ctx, "Orion", exclude=ctx.this_card):
        yield from actions.draw(2)
    yield from actions.log(ctx.this_card)
