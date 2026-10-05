"""2KIRK25 Maximum Warp (Directive). Spec: resources/scans/to_boldly_go/cards/captains/kirk/2KIRK25.md"""

from engine.cards import operation
from engine.ops import A

from ._util import ships


@operation("2KIRK25", 0, uses=[A.DRAW, A.DISCARD, A.WARP])
def engage(ctx, actions):
    """PLAY: Draw 2 cards and discard one of the drawn cards. You may warp a Ship."""
    before = list(ctx.me.hand)
    yield from actions.draw(2)
    drawn = [i for i in ctx.me.hand if i not in before]
    if drawn:
        yield from actions.discard(1, pred=lambda i: i in drawn, label="one of the drawn cards")
    ship = yield from actions.pick_card("Warp a Ship?", ships(ctx), optional=True, none_label="No")
    if ship:
        yield from actions.warp(ship)
