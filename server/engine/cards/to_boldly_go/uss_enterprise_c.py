"""2SHI09 U.S.S. Enterprise-C (Ship). Spec: resources/scans/to_boldly_go/cards/ships/2SHI09.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, has_trait, others_in_hand, warp_this_ship


@operation("2SHI09", 0, uses=[A.DEPLOY, A.BEAM, A.WARP, A.EXHAUST])
def deploy_beam_warp(ctx, actions):
    """PLAY: Deploy this ship. Up to twice: beam a card here OR warp this ship. Exhaust this ship."""
    ship = ctx.this_card
    yield from actions.deploy(ship)
    for n in (1, 2):
        options = ([("beam", "Beam a card from hand here")] if others_in_hand(ctx) else []) + \
            [("warp", "Warp this ship"), ("stop", "Stop")]
        choice = yield from actions.choose(f"Enterprise-C ({n} of 2): beam a card here or warp?", options)
        if choice == "stop":
            break
        if choice == "beam":
            yield from beam_a_card_here(ctx, actions)
        else:
            yield from actions.warp(ship)
    yield from actions.exhaust(ship)


operation("2SHI09", 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation("2SHI09", 2, uses=[A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)


@operation("2SHI09", 3, uses=[A.DISMISS, A.DISCARD, A.GAIN_RESOURCE, A.GAIN_ACTION, A.RECALL],
           requires=lambda ctx: bool(others_in_hand(ctx)))
def last_stand(ctx, actions):
    """ACTIVATION: Dismiss this ship and discard a card to gain 1 [Glory], 1 [Action] and recall a non-Time Travel
    card from your Staging Area."""
    yield from actions.dismiss(ctx.this_card)
    yield from actions.discard(1)
    yield from actions.gain_resource("glory", 1)
    yield from actions.gain_action(1)
    cards = [i for i in ctx.me.staging if not has_trait(i, "Time Travel")]
    card = yield from actions.pick_card("Recall which card from your Staging Area?", cards)
    if card:
        yield from actions.recall(card)
