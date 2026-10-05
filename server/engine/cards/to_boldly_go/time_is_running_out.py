"""2DIR01 Time Is Running Out (Directive, solo Ticking Clock challenge). Spec: resources/scans/to_boldly_go/cards/2DIR01.md"""

from engine.cards import operation
from engine.ops import A


@operation("2DIR01", 0, uses=[A.GAIN_RESOURCE, A.PUT, A.JUNK, A.DRAW, A.DISCARD, A.FORCE])
def surprise(ctx, actions):
    """SURPRISE (Bot only): Gain 2 [Glory]. Put the top card of the Supplement deck on top of the Bot deck. Junk the
    top card of the Incident deck. You draw a card and discard a card. Runs with the Bot as "me" (REQ-SOLO-87, -130)."""
    yield from actions.gain_resource("glory", 2)
    if ctx.me.reserve:
        yield from actions.put_on_deck(ctx.me.reserve[0])
    yield from actions.junk_top_incident()
    human = ctx.opponent
    if human is not None:
        yield from actions.draw(1, player=human)
        yield from actions.discard(1, player=human)
