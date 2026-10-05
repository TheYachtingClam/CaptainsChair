"""2INC05 Subspace Phenomenon (Incident). Spec: resources/scans/to_boldly_go/cards/incident/2INC05.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import count_traits


def _draw_two_keep_one(ctx, actions):
    before = list(ctx.me.hand)
    yield from actions.draw(2)
    drawn = [i for i in ctx.me.hand if i not in before]
    if drawn:
        yield from actions.discard(1, pred=lambda i: i in drawn, label="one of the drawn cards")


@operation("2INC05", 0, uses=[A.DISCARD, A.RETURN_INCIDENT, A.DRAW], cost=[DiscardFromHand(1)])
def study(ctx, actions):
    """PLAY: Discard a card to return this card. If the discarded card has [Research]/[Research Focus], draw 2 cards
    and discard one of them."""
    yield from actions.return_incident(ctx.this_card)
    if ctx.has_specialty_icon(actions.paid[0], "research"):
        yield from _draw_two_keep_one(ctx, actions)


@operation("2INC05", 1, uses=[A.RETURN_INCIDENT, A.DRAW, A.DISCARD],
           requires=lambda ctx: count_traits(ctx, "Time Travel") > 0)
def temporal_fix(ctx, actions):
    """PLAY: If you have a Time Travel in play, return this card and draw 2 cards and discard one of them."""
    yield from actions.return_incident(ctx.this_card)
    yield from _draw_two_keep_one(ctx, actions)
