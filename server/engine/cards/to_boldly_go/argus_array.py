"""2LOC03 Argus Array (Location). Spec: resources/scans/to_boldly_go/cards/location/2LOC03.md"""

from engine.cards import operation
from engine.ops import A

from ._locations import no_effect

operation("2LOC03", 0, uses=[])(no_effect)


@operation("2LOC03", 1, uses=[A.DISCARD, A.DRAW_FROM_DISCARD])
def listen(ctx, actions):
    """RESUPPLY: You may discard a card to draw a card from your Discard pile."""
    if ctx.me.hand and (yield from actions.may("Discard a card to take a card from your Discard pile?")):
        yield from actions.discard(1)
        yield from actions.draw_from_discard()
