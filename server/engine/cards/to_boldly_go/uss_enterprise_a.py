"""2KIRK05 U.S.S. Enterprise-A (Ship, Development). Spec: resources/scans/to_boldly_go/cards/captains/kirk/2KIRK05.md"""

from engine.cards import development_cost, operation
from engine.ops import A, DiscardFromHand, Spend, SpendUnless

from ._util import beam_a_card_here, is_suit, others_in_hand
from .uss_shenzhou import beam, promote, warp

development_cost("2KIRK05", SpendUnless(Spend(dilithium=6), lambda ctx: any(i.card == "2KIRK02" for i in ctx.me.log)))


@operation("2KIRK05", 0, uses=[A.DEPLOY, A.WARP, A.BEAM, A.DISCARD])
def launch(ctx, actions):
    """PLAY: Deploy this ship. Warp this ship OR beam a card here. You may discard a card to beam a (different) card
    here."""
    ship = ctx.this_card
    yield from actions.deploy(ship)
    options = [("warp", "Warp this ship")] + ([("beam", "Beam a card here")] if others_in_hand(ctx) else [])
    choice = options[0][0] if len(options) == 1 else (yield from actions.choose("Warp or beam a card here?", options))
    if choice == "warp":
        yield from actions.warp(ship)
    else:
        yield from beam_a_card_here(ctx, actions)
    if len(others_in_hand(ctx)) >= 2 and (yield from actions.may("Discard a card to beam another card here?")):
        yield from actions.discard(1)
        yield from beam_a_card_here(ctx, actions)


operation("2KIRK05", 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp)
operation("2KIRK05", 2, uses=[A.BEAM], cost=[DiscardFromHand(1)],
          requires=lambda ctx: len(others_in_hand(ctx)) >= 2)(beam)
operation("2KIRK05", 3, uses=[A.PROMOTE], requires=lambda ctx: any(is_suit(i, "Person") for i in ctx.me.hand))(promote)
