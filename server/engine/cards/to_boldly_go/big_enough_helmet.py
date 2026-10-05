"""2REB03 Big Enough Helmet (Cargo, Development). Spec: resources/scans/to_boldly_go/cards/captains/rebner/2REB03.md"""

from engine.cards import development_cost, operation
from engine.ops import A, EffectCost


def _opponent_may_draw(ctx, actions):
    """DEV. COST: Your opponent may draw 2 cards. Cadet: there is no one to draw."""
    opp = ctx.opponent
    if opp is not None and (yield from actions.may("Draw 2 cards (Rebner's Big Enough Helmet)?", seat=opp.seat)):
        yield from actions.draw(2, player=opp)


development_cost("2REB03", EffectCost(lambda ctx: True, _opponent_may_draw, (A.DRAW, A.FORCE),
                                      "your opponent may draw 2 cards"))


@operation("2REB03", 0, uses=[A.GAIN_RESOURCE, A.REFRESH])
def generous(ctx, actions):
    """PLAY: Gain 1 [Latinum], 1 [Dilithium], and 1 [Glory]. You may refresh your Captain."""
    for kind in ("latinum", "dilithium", "glory"):
        yield from actions.gain_resource(kind, 1)
    if ctx.me.captain.exhausted and (yield from actions.may("Refresh your Captain?")):
        yield from actions.refresh(ctx.me.captain)
