"""2ALL11 Salt Vampires (Ally). Spec: resources/scans/to_boldly_go/cards/ally/2ALL11.md"""

from engine.cards import operation
from engine.ops import A


@operation("2ALL11", 0, uses=[A.DRAW])
def draw_two(ctx, actions):
    """PLAY: Draw 2 cards."""
    yield from actions.draw(2)


@operation("2ALL11", 1, uses=[A.LOG])
def feed(ctx, actions):
    """CLEAN-UP: Log a card from your Staging Area (can be this card). Mandatory."""
    card = yield from actions.pick_card("Salt Vampires: log a card from your Staging Area.", list(ctx.me.staging))
    if card:
        yield from actions.log(card)
