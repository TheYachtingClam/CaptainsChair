"""2SHI11 Vor'cha Attack Cruiser (Ship). Spec: resources/scans/to_boldly_go/cards/ships/2SHI11.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import (beam_a_card_here, can_discard_then_beam, deploy_and_warp_this, others_in_hand,
                    send_team_to_this_ship, warp_this_ship)


@operation("2SHI11", 0, uses=[A.DEPLOY, A.WARP, A.DISCARD, A.SEND_AWAY_TEAM])
def deploy_warp_send(ctx, actions):
    """PLAY: Deploy and warp this ship. You may discard a card to send an [Away Team] to this ship's Location,
    ignoring any opponent Ship."""
    yield from deploy_and_warp_this(ctx, actions)
    loc = ctx.location_of(ctx.this_card)
    if loc is not None and others_in_hand(ctx) and (
            yield from actions.may(f"Discard a card to send an Away Team to {ctx.name(loc)}?")):
        yield from actions.discard(1)
        yield from actions.send_away_team(1, target=loc)


operation("2SHI11", 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("2SHI11", 2, uses=[A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)
operation("2SHI11", 3, uses=[A.SEND_AWAY_TEAM])(send_team_to_this_ship)
