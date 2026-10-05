"""2SHI05 Holographic Drone Ship (Ship). Spec: resources/scans/to_boldly_go/cards/ships/2SHI05.md
The first PLAY duplicates, which arrives in Step 6."""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import deploy_and_warp_this, has_trait, warp_this_ship

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
