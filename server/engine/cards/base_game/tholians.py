"""1ALL13 Tholians (Ally). Spec: resources/scans/base_game/cards/ally/1ALL13.md"""

from engine.cards import operation
from engine.ops import A


@operation("1ALL13", 0, uses=[A.DRAW, A.GAIN_RESOURCE, A.LOG])
def web(ctx, actions):
    """PLAY: You may draw a card. Gain 1 [Latinum] and 2 [Dilithium] for each controlled Location you have in play.
    Log this card."""
    if (yield from actions.may("Draw a card?")):
        yield from actions.draw(1)
    n = len(ctx.controlled_locations())
    if n:
        yield from actions.gain_resource("latinum", n)
        yield from actions.gain_resource("dilithium", 2 * n)
    yield from actions.log(ctx.this_card)
