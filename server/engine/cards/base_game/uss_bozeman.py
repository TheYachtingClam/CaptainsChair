"""1PIC10 U.S.S. Bozeman (Ship, Development). Spec: resources/scans/base_game/cards/captains/picard/1PIC10.md"""

from engine.cards import development_cost, operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, non_time_travel_in_staging, warp_this_ship

development_cost("1PIC10", Spend(dilithium=5))


@operation("1PIC10", 0, uses=[A.DEPLOY, A.ENLIST_DEVELOPMENT])
def out_of_the_loop(ctx, actions):
    """PLAY: Deploy this ship. You may enlist a Development."""
    yield from actions.deploy(ctx.this_card)
    if ctx.me.development and (yield from actions.may("Enlist a Development?")):
        yield from actions.enlist_development()


@operation("1PIC10", 1, uses=[A.RECALL],
           requires=lambda ctx: ctx.track("research") >= 6 and bool(non_time_travel_in_staging(ctx)))
def causality(ctx, actions):
    """PLAY: Requires [Research] 6. Recall a non-Time Travel card from your Staging Area."""
    card = yield from actions.pick_card("Recall which card from your Staging Area?", non_time_travel_in_staging(ctx))
    yield from actions.recall(card)


operation("1PIC10", 2, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("1PIC10", 3, uses=[A.DISCARD, A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)
