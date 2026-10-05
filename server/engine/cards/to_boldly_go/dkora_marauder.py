"""2SHI02 D'Kora Marauder (Ship). Spec: resources/scans/to_boldly_go/cards/ships/2SHI02.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, send_team_to_this_ship, warp_this_ship

operation("2SHI02", 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("2SHI02", 2, uses=[A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)
operation("2SHI02", 3, uses=[A.SEND_AWAY_TEAM], cost=[Spend(latinum=1)])(send_team_to_this_ship)


@operation("2SHI02", 0, uses=[A.DEPLOY, A.ATTACK, A.STEAL])
def raid(ctx, actions):
    """ATTACK PLAY: Deploy this ship. Steal 1 [Latinum]."""
    yield from actions.deploy(ctx.this_card)
    if (yield from actions.attack()):
        yield from actions.steal("latinum", 1)
