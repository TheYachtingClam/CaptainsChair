"""2SOV24 Ti'Mur (Ship). Spec: resources/scans/to_boldly_go/cards/captains/soval/2SOV24.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, deploy_and_warp_this, others_in_hand, warp_this_ship


@operation("2SOV24", 0, uses=[A.DEPLOY, A.DISCARD, A.GAIN_SPECIALTY])
def launch(ctx, actions):
    """PLAY: Deploy this ship. You may discard a card to gain 1 [Military]."""
    yield from actions.deploy(ctx.this_card)
    if others_in_hand(ctx) and (yield from actions.may("Discard a card to gain 1 Military?")):
        yield from actions.discard(1)
        yield from actions.gain_specialty("military", 1)


@operation("2SOV24", 1, uses=[A.DEPLOY, A.WARP, A.SEND_AWAY_TEAM], requires=lambda ctx: ctx.track("research") >= 5)
def survey(ctx, actions):
    """PLAY: Requires [Research] 5. Deploy and warp this ship. You may send an [Away Team] to this ship's Location."""
    yield from deploy_and_warp_this(ctx, actions)
    loc = ctx.location_of(ctx.this_card)
    if loc is not None and (yield from actions.may(f"Send an Away Team to {ctx.name(loc)}?")):
        yield from actions.send_away_team(1, target=loc)


operation("2SOV24", 2, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("2SOV24", 3, uses=[A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)
