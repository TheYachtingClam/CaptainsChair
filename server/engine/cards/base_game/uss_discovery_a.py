"""1BUR03 U.S.S. Discovery-A (Ship). Spec: resources/scans/base_game/cards/captains/burnham/1BUR03.md"""

from engine import cards as registry
from engine.cards import operation
from engine.cards.to_boldly_go.uss_shenzhou import promote
from engine.ops import A, DiscardFromHand

from ._util import beam_a_card_here, can_discard_then_beam, is_suit, others_in_hand, people_in_hand


@operation("1BUR03", 0, uses=[A.DEPLOY, A.DISCARD, A.FREE_PLAY])
def launch(ctx, actions):
    """PLAY: Deploy this ship. You may discard a card to free play a Person."""
    yield from actions.deploy(ctx.this_card)
    if len(others_in_hand(ctx)) >= 2 and others_in_hand(ctx, lambda i: is_suit(i, "Person")) and (
            yield from actions.may("Discard a card to free play a Person?")):
        yield from actions.discard(1)
        person = yield from actions.pick_card("Free play which Person?",
                                              actions.free_play_candidates(lambda i: is_suit(i, "Person")))
        if person:
            yield from actions.free_play(person)


@operation("1BUR03", 1, uses=[A.WARP, A.REFRESH])
def spore_jump(ctx, actions):
    """ACTIVATION: Warp this ship, then refresh this ship."""
    yield from actions.warp(ctx.this_card)
    yield from actions.refresh(ctx.this_card)


operation("1BUR03", 2, uses=[A.DISCARD, A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)
operation("1BUR03", 3, uses=[A.PROMOTE], requires=lambda ctx: bool(people_in_hand(ctx)))(promote)

registry.CANNOT_BE_STOLEN["1BUR03"] = "dilithium"  # PASSIVE: Your [Dilithium] cannot be stolen.
