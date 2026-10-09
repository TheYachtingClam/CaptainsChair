"""1KOL09 I.K.S. Devisor (Ship, Development). Spec: resources/scans/base_game/cards/captains/koloth/1KOL09.md"""

from engine.cards import development_cost, operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, send_team_here, warp_this_ship

development_cost("1KOL09", Spend(dilithium=5))


@operation("1KOL09", 0, uses=[A.DEPLOY, A.GAIN_RESOURCE])
def flagship(ctx, actions):
    """PLAY: Deploy this ship. Gain 1 [Glory]."""
    yield from actions.deploy(ctx.this_card)
    yield from actions.gain_resource("glory", 1)


operation("1KOL09", 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("1KOL09", 2, uses=[A.DISCARD, A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)
operation("1KOL09", 3, uses=[A.SEND_AWAY_TEAM], requires=lambda ctx: ctx.location_of(ctx.this_card) is not None)(send_team_here)
