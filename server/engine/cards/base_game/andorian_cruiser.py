"""1SHR07 Andorian Cruiser (Ship, Development). Spec: resources/scans/base_game/cards/captains/shran/1SHR07.md"""

from engine.cards import development_cost, operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, send_team_here, warp_this_ship

development_cost("1SHR07", Spend(dilithium=5))


@operation("1SHR07", 0, uses=[A.DEPLOY, A.SPEND, A.WARP])
def patrol(ctx, actions):
    """PLAY: Deploy this ship. You may spend 1 [Dilithium] to warp this ship."""
    yield from actions.deploy(ctx.this_card)
    if actions.can_spend(dilithium=1) and (yield from actions.may("Spend 1 Dilithium to warp this ship?")):
        yield from actions.spend(dilithium=1)
        yield from actions.warp(ctx.this_card)


operation("1SHR07", 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("1SHR07", 2, uses=[A.DISCARD, A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)
operation("1SHR07", 3, uses=[A.SEND_AWAY_TEAM], requires=lambda ctx: ctx.location_of(ctx.this_card) is not None)(send_team_here)
