"""1SHI05 K't'inga Battlecruiser (Ship). Spec: resources/scans/base_game/cards/ships/1SHI05.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, warp_this_ship


@operation("1SHI05", 0, uses=[A.DEPLOY, A.SEND_AWAY_TEAM])
def landing(ctx, actions):
    """PLAY: Deploy this ship. You may send an [Away Team] to a Location."""
    yield from actions.deploy(ctx.this_card)
    if actions.away_targets() and (yield from actions.may("Send an Away Team to a Location?")):
        yield from actions.send_away_team(1)


operation("1SHI05", 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("1SHI05", 2, uses=[A.DISCARD, A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)
