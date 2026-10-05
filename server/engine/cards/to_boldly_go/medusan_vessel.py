"""2SHI07 Medusan Vessel (Ship). Spec: resources/scans/to_boldly_go/cards/ships/2SHI07.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, has_trait, others_in_hand, warp_this_ship


@operation("2SHI07", 0, uses=[A.DEPLOY, A.DISCARD, A.SCAN_FOR])
def deploy_and_scan(ctx, actions):
    """PLAY: Deploy this ship. You may discard a card to scan for a Telepath."""
    yield from actions.deploy(ctx.this_card)
    if others_in_hand(ctx) and (yield from actions.may("Discard a card to scan for a Telepath?")):
        yield from actions.discard(1)
        yield from actions.scan_for(lambda i: has_trait(i, "Telepath"), "a Telepath")


operation("2SHI07", 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("2SHI07", 2, uses=[A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)
