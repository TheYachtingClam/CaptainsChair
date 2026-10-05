"""2SHI05 Holographic Drone Ship (Ship). Spec: resources/scans/to_boldly_go/cards/ships/2SHI05.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import deploy_and_warp_this, has_trait, is_suit, warp_this_ship

operation("2SHI05", 1, uses=[A.DEPLOY, A.WARP],
          cost=[DiscardFromHand(1, lambda ctx, i: has_trait(i, "Telepath"), "a Telepath")])(deploy_and_warp_this)


@operation("2SHI05", 2, uses=[A.DISMISS, A.GAIN_RESOURCE])
def dismiss_for_glory(ctx, actions):
    """CLEAN-UP: You may dismiss this ship to gain 2 [Glory]. It must be deployed: the Staging Area cannot be
    dismissed from (KW-DSM-04)."""
    if ctx.this_card in ctx.me.fleet and (yield from actions.may("Dismiss the Holographic Drone Ship to gain 2 Glory?")):
        yield from actions.dismiss(ctx.this_card)
        yield from actions.gain_resource("glory", 2)


operation("2SHI05", 3, uses=[A.WARP])(warp_this_ship)


@operation("2SHI05", 0, uses=[A.DRAW, A.DUPLICATE], requires=lambda ctx: ctx.track("research") >= 7)
def mimic(ctx, actions):
    """PLAY: Requires [Research] 7. Draw a card. Duplicate a play operation of a non-Time Travel Ship from the Market
    or deployed by any player. Ruling: duplicating "deploy this ship" deploys the Drone Ship itself (KW-DUP-04)."""
    yield from actions.draw(1)
    candidates = [i for i in [ctx.state.market.get("Ship"), *ctx.me.fleet,
                              *(ctx.opponent.fleet if ctx.opponent else [])]
                  if i is not None and is_suit(i, "Ship") and not has_trait(i, "Time Travel")]
    yield from actions.duplicate(candidates, label="a Ship", optional=False)
