"""1SHI09 U.S.S. Enterprise-C (Ship), the older Core Box version. Spec: resources/scans/base_game/cards/ships/1SHI09.md
To Boldly Go's version (2SHI09) has a different PLAY."""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import (beam_a_card_here, can_discard_then_beam, non_time_travel_in_staging, others_in_hand,
                    warp_this_ship)


@operation("1SHI09", 0, uses=[A.DEPLOY, A.BEAM])
def launch(ctx, actions):
    """PLAY: Deploy this ship. You may beam a card here."""
    yield from actions.deploy(ctx.this_card)
    card = yield from actions.pick_card("Beam a card here?", others_in_hand(ctx), optional=True, none_label="No")
    if card:
        yield from actions.beam(card, ctx.this_card)


operation("1SHI09", 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("1SHI09", 2, uses=[A.DISCARD, A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)


@operation("1SHI09", 3, uses=[A.DISMISS, A.DISCARD, A.GAIN_RESOURCE, A.GAIN_ACTION, A.RECALL],
           requires=lambda ctx: bool(others_in_hand(ctx)))
def last_stand(ctx, actions):
    """ACTIVATION: Dismiss this ship and discard a card to gain 1 [Glory], 1 [Action] and recall a non-Time Travel
    card from your Staging Area."""
    yield from actions.dismiss(ctx.this_card)
    yield from actions.discard(1)
    yield from actions.gain_resource("glory", 1)
    yield from actions.gain_action(1)
    card = yield from actions.pick_card("Recall which card from your Staging Area?", non_time_travel_in_staging(ctx))
    if card:
        yield from actions.recall(card)
