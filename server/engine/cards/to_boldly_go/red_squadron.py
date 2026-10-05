"""2ALL10 Red Squadron (Ally). Spec: resources/scans/to_boldly_go/cards/ally/2ALL10.md
The second PLAY is an attack and arrives in Step 4."""

from engine.cards import operation
from engine.ops import A

from ._util import ships


@operation("2ALL10", 0, uses=[A.DRAW, A.DISCARD, A.BEAM, A.WARP])
def scramble(ctx, actions):
    """PLAY: Draw 2 cards and discard one of the drawn cards. You may beam a card from your Staging Area to a Ship
    (can be this card). You may warp a Ship."""
    before = list(ctx.me.hand)
    yield from actions.draw(2)
    drawn = [i for i in ctx.me.hand if i not in before]
    if drawn:
        yield from actions.discard(1, pred=lambda i: i in drawn, label="one of the drawn cards")
    your_ships = ships(ctx)
    if your_ships and ctx.me.staging:
        card = yield from actions.pick_card("Beam a card from your Staging Area to a Ship?", list(ctx.me.staging),
                                            optional=True, none_label="No")
        if card:
            ship = yield from actions.pick_card(f"Beam {ctx.name(card)} to which Ship?", your_ships)
            yield from actions.beam(card, ship)
    if your_ships:
        ship = yield from actions.pick_card("Warp a Ship?", ships(ctx), optional=True, none_label="No")
        if ship:
            yield from actions.warp(ship)
