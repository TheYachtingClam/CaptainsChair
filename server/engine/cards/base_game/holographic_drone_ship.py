"""1SHI04 Holographic Drone Ship (Ship), the older Core Box version. Spec: resources/scans/base_game/cards/ships/1SHI04.md
To Boldly Go's version (2SHI05) cannot duplicate a Time Travel Ship and is dismissed in Clean-up, not by an Activation."""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import deploy_and_warp_this, has_trait, is_suit, warp_this_ship


@operation("1SHI04", 0, uses=[A.DRAW, A.DUPLICATE], requires=lambda ctx: ctx.track("research") >= 7)
def mimic(ctx, actions):
    """PLAY: Requires [Research] 7. Draw a card. Duplicate a play operation of a Ship from the Market or any player's
    Fleet Area. Duplicating "deploy this ship" deploys the Drone Ship itself (KW-DUP-04)."""
    yield from actions.draw(1)
    candidates = [i for i in [ctx.state.market.get("Ship"), *ctx.me.fleet,
                              *(ctx.opponent.fleet if ctx.opponent else [])]
                  if i is not None and is_suit(i, "Ship")]
    yield from actions.duplicate(candidates, label="a Ship", optional=False)


operation("1SHI04", 1, uses=[A.DISCARD, A.DEPLOY, A.WARP],
          cost=[DiscardFromHand(1, lambda ctx, i: has_trait(i, "Telepath"), "a Telepath")])(deploy_and_warp_this)
operation("1SHI04", 2, uses=[A.WARP])(warp_this_ship)


@operation("1SHI04", 3, uses=[A.DISMISS, A.GAIN_RESOURCE])
def burn_out(ctx, actions):
    """ACTIVATION: Dismiss this ship. Gain 2 [Glory]."""
    yield from actions.dismiss(ctx.this_card)
    yield from actions.gain_resource("glory", 2)
