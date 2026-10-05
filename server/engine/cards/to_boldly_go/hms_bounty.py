"""2KIRK11 H.M.S. Bounty (Ship). Spec: resources/scans/to_boldly_go/cards/captains/kirk/2KIRK11.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, is_suit, warp_this_ship


@operation("2KIRK11", 0, uses=[A.DEPLOY])
def deploy(ctx, actions):
    """PLAY: Deploy this ship."""
    yield from actions.deploy(ctx.this_card)


@operation("2KIRK11", 1, uses=[A.DEPLOY, A.DISCARD, A.SEND_AWAY_TEAM], requires=lambda ctx: ctx.track("influence") >= 5)
def cloaked_approach(ctx, actions):
    """PLAY: Requires [Influence] 5. Deploy this ship. You may discard an Incident to send an [Away Team] to a Location,
    ignoring any opponent Ship."""
    yield from actions.deploy(ctx.this_card)
    if any(is_suit(i, "Incident") for i in ctx.me.hand) and (
            yield from actions.may("Discard an Incident to send an Away Team, ignoring opponent Ships?")):
        yield from actions.discard(1, pred=lambda i: is_suit(i, "Incident"), label="an Incident")
        yield from actions.send_away_team(1, ignore_ships=True)


operation("2KIRK11", 2, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("2KIRK11", 3, uses=[A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)
