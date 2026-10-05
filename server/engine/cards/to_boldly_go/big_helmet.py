"""2REB21 and 2REB22 Big Helmet (Cargo), two identical copies. Spec: resources/scans/to_boldly_go/cards/captains/rebner/2REB21.md"""

from engine.cards import operation
from engine.ops import A

from ._util import is_suit
from .uss_shenzhou import promote

IDS = ("2REB21", "2REB22")


@operation(IDS, 0, uses=[A.GAIN_RESOURCE])
def latinum(ctx, actions):
    """PLAY: Gain 1 [Latinum]."""
    yield from actions.gain_resource("latinum", 1)


@operation(IDS, 1, uses=[A.DRAW, A.DISCARD])
def rummage(ctx, actions):
    """PLAY: Draw 2 cards and discard 1 of them."""
    before = {i.uid for i in ctx.me.hand}
    yield from actions.draw(2)
    drawn = {i.uid for i in ctx.me.hand} - before
    if drawn:
        yield from actions.discard(1, pred=lambda i: i.uid in drawn, label="one of the drawn cards")


operation(IDS, 2, uses=[A.PROMOTE], requires=lambda ctx: any(is_suit(i, "Person") for i in ctx.me.hand))(promote)
