"""1SHR01 Thy'lek Shran (Captain). Spec: resources/scans/base_game/cards/captains/shran/1SHR01.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import is_suit


@operation("1SHR01", 0, uses=[A.GAIN_RESOURCE])
def supply_lines(ctx, actions):
    """RESUPPLY: Gain 1 [Dilithium] per Cargo you have in play."""
    n = ctx.count_in_play(lambda i: is_suit(i, "Cargo"))
    if n:
        yield from actions.gain_resource("dilithium", n)


@operation("1SHR01", 1, uses=[A.DISCARD, A.SEND_AWAY_TEAM],
           cost=[DiscardFromHand(1, lambda ctx, i: is_suit(i, "Cargo"), "a Cargo")],
           requires=lambda ctx: bool(ctx.controlled_locations()))
def garrison(ctx, actions):
    """ACTIVATION: Discard a Cargo to send an [Away Team] to a controlled Location."""
    yield from actions.send_away_team(1, lambda loc: any(c.uid == loc.uid for c in ctx.controlled_locations()))
