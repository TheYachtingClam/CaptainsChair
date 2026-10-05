"""3FRE02 U.S.S. Cerritos and its identical copy 3FRE11 U.S.S. Carlsbad (Ships). Spec: resources/scans/second_contact/cards/captains/freeman/3FRE02.md"""

from engine.cards import operation
from engine.cards.to_boldly_go.uss_shenzhou import promote
from engine.ops import A, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, is_suit, warp_this_ship

IDS = ("3FRE02", "3FRE11")
TRACKS = ("research", "influence", "military")


@operation(IDS, 0, uses=[A.DEPLOY, A.BEAM, A.SPEND, A.GAIN_SPECIALTY, A.EXHAUST])
def california_class(ctx, actions):
    """PLAY: Deploy this ship. You may beam a card here from your hand or Discard pile. You may spend 1 [Dilithium] to
    gain 1 [Research]/[Influence]/[Military], whichever is the lowest. Exhaust this ship."""
    ship = ctx.this_card
    yield from actions.deploy(ship)
    cards = [i for i in ctx.me.hand + ctx.me.discard if i is not ship]
    card = yield from actions.pick_card("Beam a card here?", cards, optional=True, none_label="No")
    if card:
        yield from actions.beam(card, ship)
    if actions.can_spend(dilithium=1) and (yield from actions.may("Spend 1 Dilithium to gain 1 on your lowest track?")):
        yield from actions.spend(dilithium=1)
        lowest = min(TRACKS, key=lambda t: ctx.track(t))  # ties go Research, Influence, Military
        yield from actions.gain_specialty(lowest, 1)
    if ship in ctx.me.fleet:
        yield from actions.exhaust(ship)


operation(IDS, 1, uses=[A.WARP], cost=[Spend(dilithium=1)])(warp_this_ship)
operation(IDS, 2, uses=[A.DISCARD, A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)(beam_a_card_here)
operation(IDS, 3, uses=[A.PROMOTE], requires=lambda ctx: any(is_suit(i, "Person") for i in ctx.me.hand))(promote)
