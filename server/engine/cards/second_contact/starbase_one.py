"""3PIK03 Starbase One (Location). Spec: resources/scans/second_contact/cards/captains/pike/3PIK03.md"""

from engine.cards import operation
from engine.cards.to_boldly_go.uss_shenzhou import promote
from engine.ops import A

from ._util import is_suit


@operation("3PIK03", 0, uses=[A.GAIN_ACTION])
def headquarters(ctx, actions):
    """CONTROL: Gain an [Action]."""
    yield from actions.gain_action(1)


def _ships(ctx) -> int:
    return ctx.count_in_play(lambda i: is_suit(i, "Ship"))


@operation("3PIK03", 1, uses=[A.DRAW], requires=lambda ctx: _ships(ctx) >= 2)
def fleet_briefing(ctx, actions):
    """ACTIVATION: For every 2 Ship you have in play, draw a card (max 3 cards). Offered only with 2 or more Ships in
    play, so it is never activated for nothing."""
    yield from actions.draw(min(3, _ships(ctx) // 2))


operation("3PIK03", 2, uses=[A.PROMOTE], requires=lambda ctx: any(is_suit(i, "Person") for i in ctx.me.hand))(promote)
