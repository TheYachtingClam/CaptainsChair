"""2ARC03 NX-01 Enterprise (Ship). Spec: resources/scans/to_boldly_go/cards/captains/archer/2ARC03.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import is_suit, others_in_hand, warp_this_ship
from .uss_shenzhou import promote


@operation("2ARC03", 0, uses=[A.DEPLOY, A.EXHAUST, A.WARP])
def launch(ctx, actions):
    """PLAY: Deploy this ship. You may exhaust a Duty Officer to warp this ship."""
    yield from actions.deploy(ctx.this_card)
    ready = [i for i in ctx.me.duty if not i.exhausted]
    officer = yield from actions.pick_card("Exhaust a Duty Officer to warp the NX-01 Enterprise?", ready, optional=True,
                                           none_label="No")
    if officer:
        yield from actions.exhaust(officer)
        yield from actions.warp(ctx.this_card)


operation("2ARC03", 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)


@operation("2ARC03", 2, uses=[A.BEAM], cost=[Spend(dilithium=1)], requires=lambda ctx: bool(others_in_hand(ctx)))
def beam_aboard(ctx, actions):
    """ACTIVATION: Spend 1 [Dilithium] to beam a card here."""
    card = yield from actions.pick_card("Beam which card to the NX-01 Enterprise?", others_in_hand(ctx))
    yield from actions.beam(card, ctx.this_card)


operation("2ARC03", 3, uses=[A.PROMOTE], requires=lambda ctx: any(is_suit(i, "Person") for i in ctx.me.hand))(promote)
