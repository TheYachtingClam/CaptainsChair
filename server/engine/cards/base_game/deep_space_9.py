"""1SIS03 Deep Space 9 (Ship). Spec: resources/scans/base_game/cards/captains/sisko/1SIS03.md"""

from engine import cards as registry
from engine.cards import operation
from engine.cards.to_boldly_go.uss_shenzhou import promote
from engine.ops import A, DiscardFromHand

from ._util import beamed_here, others_in_hand, people_in_hand

registry.CANNOT_WARP.add("1SIS03")  # PASSIVE: This ship cannot be warped.


@operation("1SIS03", 0, uses=[A.DEPLOY])
def open_the_station(ctx, actions):
    """PLAY: Deploy this card."""
    yield from actions.deploy(ctx.this_card)


@operation("1SIS03", 1, uses=[A.DISCARD, A.BEAM, A.RECALL], cost=[DiscardFromHand(1)],
           requires=lambda ctx: len(others_in_hand(ctx)) >= 2 or bool(beamed_here(ctx)))
def promenade(ctx, actions):
    """ACTIVATION: Discard a card to either: beam a card here OR recall a card beamed here."""
    options = ([("beam", "Beam a card here")] if others_in_hand(ctx) else []) + \
        ([("recall", "Recall a card beamed here")] if beamed_here(ctx) else [])
    if not options:
        return
    choice = options[0][0] if len(options) == 1 else (yield from actions.choose("Deep Space 9:", options))
    if choice == "beam":
        card = yield from actions.pick_card("Beam which card to Deep Space 9?", others_in_hand(ctx))
        yield from actions.beam(card, ctx.this_card)
    else:
        card = yield from actions.pick_card("Recall which card?", beamed_here(ctx))
        yield from actions.recall(card)


operation("1SIS03", 2, uses=[A.PROMOTE], requires=lambda ctx: bool(people_in_hand(ctx)))(promote)
