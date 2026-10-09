"""1SIS13 Miles O'Brien (Person). Spec: resources/scans/base_game/cards/captains/sisko/1SIS13.md"""

from engine import cards as registry
from engine.cards import operation
from engine.ops import A, Spend

from ._util import draw_two_discard_one, is_suit

registry.CANNOT_PROMOTE.add("1SIS13")  # SPECIAL: THIS CARD CANNOT BE PROMOTED.


@operation("1SIS13", 0, uses=[A.DRAW, A.DISCARD])
def repairs(ctx, actions):
    """PLAY: Draw 2 cards and discard 1 of them."""
    yield from draw_two_discard_one(ctx, actions)


@operation("1SIS13", 1, uses=[A.DRAW_FROM_DISCARD, A.FREE_PLAY, A.DRAW], cost=[Spend(dilithium=1)],
           requires=lambda ctx: ctx.track("military") >= 5 and any(is_suit(i, "Ship") for i in ctx.me.discard))
def refit(ctx, actions):
    """PLAY: Requires [Military] 5. Spend 1 [Dilithium] to draw a Ship from your Discard pile and free play it. Then,
    draw a card."""
    before = [i.uid for i in ctx.me.hand]
    yield from actions.draw_from_discard(lambda i: is_suit(i, "Ship"), "a Ship")
    ship = next((i for i in ctx.me.hand if i.uid not in before), None)
    if ship is not None and actions.free_play_candidates(lambda i: i.uid == ship.uid):
        yield from actions.free_play(ship)
    yield from actions.draw(1)
