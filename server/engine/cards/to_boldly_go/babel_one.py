"""2LOC12 Babel One (Location). Spec: resources/scans/to_boldly_go/cards/location/2LOC12.md"""

from engine.cards import endgame, operation
from engine.ops import A

from ._locations import no_effect
from ._util import count_traits, ctx_for, has_trait

operation("2LOC12", 0, uses=[])(no_effect)


@operation("2LOC12", 1, uses=[A.DRAW])
def conference(ctx, actions):
    """RESUPPLY: Draw a card for each Communication you have in play (excluding this card, max 3)."""
    n = min(3, count_traits(ctx, "Communication", exclude=ctx.this_card))
    if n:
        yield from actions.draw(n)


@endgame("2LOC12")
def diplomats(state, player):
    """ENDGAME: Requires [Influence] 6. Score 1 [VP] for each Communication/Ambassador you have in play."""
    if player.tracks["influence"] < 6:
        return 0
    ctx = ctx_for(state, player)
    return ctx.count_in_play(lambda i: has_trait(i, "Communication", "Ambassador"))
