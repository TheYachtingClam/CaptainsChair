"""1SIS25 U.S.S. Rio Grande (Ship). Spec: resources/scans/base_game/cards/captains/sisko/1SIS25.md"""

from engine.cards import operation
from engine.cards.base_game.type_7_shuttlecraft import ferry
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, locations_with_your_ship, warp_this_ship


@operation("1SIS25", 0, uses=[A.DEPLOY])
def launch(ctx, actions):
    """PLAY: Deploy this ship."""
    yield from actions.deploy(ctx.this_card)


operation("1SIS25", 1, uses=[A.GAIN_RESOURCE, A.BEAM, A.RECALL])(ferry)


@operation("1SIS25", 2, uses=[A.SEND_AWAY_TEAM], requires=lambda ctx: bool(locations_with_your_ship(ctx)))
def runabout(ctx, actions):
    """PLAY: Send an [Away Team] to a Location where you have a Ship."""
    yield from actions.send_away_team(1, lambda loc: bool(ctx.ships_at(loc)))


operation("1SIS25", 3, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("1SIS25", 4, uses=[A.DISCARD, A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)
