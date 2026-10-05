"""2SHI03 D'Kyr Cruiser (Ship), and Soval's Seleya (D'Kyr) 2SOV10 with the same first four operations.
Spec: resources/scans/to_boldly_go/cards/ships/2SHI03.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, deploy_and_warp_this, others_in_hand, warp_this_ship

IDS = ("2SHI03", "2SOV10")


@operation(IDS, 0, uses=[A.DEPLOY, A.WARP, A.DISCARD, A.GAIN_SPECIALTY])
def deploy_warp_research(ctx, actions):
    """PLAY: Deploy and warp this ship. You may discard a card to gain 1 [Research]."""
    yield from deploy_and_warp_this(ctx, actions)
    if others_in_hand(ctx) and (yield from actions.may("Discard a card to gain 1 Research?")):
        yield from actions.discard(1)
        yield from actions.gain_specialty("research", 1)


@operation(IDS, 1, uses=[A.DEPLOY, A.WARP, A.SEND_AWAY_TEAM], requires=lambda ctx: ctx.track("military") >= 5)
def deploy_warp_send(ctx, actions):
    """PLAY: Requires [Military] 5. Deploy and warp this ship. You may send an [Away Team] to this ship's Location."""
    yield from deploy_and_warp_this(ctx, actions)
    loc = ctx.location_of(ctx.this_card)
    if loc is not None and (yield from actions.may(f"Send an Away Team to {ctx.name(loc)}?")):
        yield from actions.send_away_team(1, target=loc)


operation(IDS, 2, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation(IDS, 3, uses=[A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)
