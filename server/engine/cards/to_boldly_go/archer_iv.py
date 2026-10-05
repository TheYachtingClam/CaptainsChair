"""2LOC02 Archer IV (Location). Spec: resources/scans/to_boldly_go/cards/location/2LOC02.md"""

from engine.cards import operation
from engine.ops import A

from ._locations import no_effect

operation("2LOC02", 0, uses=[])(no_effect)


@operation("2LOC02", 1, uses=[A.DRAW, A.DISCARD])
def resupply(ctx, actions):
    """RESUPPLY: Draw a card, then discard a card."""
    yield from actions.draw(1)
    yield from actions.discard(1)
