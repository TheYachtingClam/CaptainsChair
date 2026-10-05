"""3PER10 Jennifer Sh'reyan (Person). Spec: resources/scans/second_contact/cards/person/3PER10.md
The SUPPORT arrives in Step 7."""

from engine.cards import operation
from engine.ops import A

from ._util import ships


@operation("3PER10", 0, uses=[A.BEAM, A.GAIN_RESOURCE, A.RECALL, A.WARP], requires=lambda ctx: bool(ships(ctx)))
def pilot(ctx, actions):
    """PLAY: Beam this card to a deployed Ship to gain 2 [Dilithium]. You may recall another card beamed to that
    Ship. You may warp that Ship."""
    ship = yield from actions.pick_card("Beam Jennifer Sh'reyan to which Ship?", ships(ctx))
    yield from actions.beam(ctx.this_card, ship)
    yield from actions.gain_resource("dilithium", 2)
    others = [b for b in ship.beamed if b is not ctx.this_card]
    card = yield from actions.pick_card("Recall another card beamed to that Ship?", others, optional=True, none_label="No")
    if card:
        yield from actions.recall(card)
    if (yield from actions.may(f"Warp {ctx.name(ship)}?")):
        yield from actions.warp(ship)


@operation("3PER10", 2, uses=[A.WARP, A.DRAW, A.DISCARD], requires=lambda ctx: bool(ships(ctx)))
def evasive(ctx, actions):
    """ACTIVATION: Warp a Ship to draw 2 cards and discard one of them."""
    ship = yield from actions.pick_card("Warp which Ship?", ships(ctx))
    yield from actions.warp(ship)
    before = list(ctx.me.hand)
    yield from actions.draw(2)
    drawn = [i for i in ctx.me.hand if i not in before]
    if drawn:
        yield from actions.discard(1, pred=lambda i: i in drawn, label="one of the drawn cards")
