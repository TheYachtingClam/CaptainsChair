"""2KIRK01 James T. Kirk (Captain). Spec: resources/scans/to_boldly_go/cards/captains/kirk/2KIRK01.md"""

from engine.cards import endgame, operation
from engine.ops import A, DiscardFromHand, PutOnDeck

from ._util import has_trait, is_suit


@operation("2KIRK01", 0, uses=[A.DISCARD, A.GAIN_SPECIALTY], cost=[DiscardFromHand(1)],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and has_trait(ctx.event_card, "Klingon"))
def respect(ctx, actions):
    """REACTION: After putting a Klingon into play, discard a card to gain 1 [Military]."""
    yield from actions.gain_specialty("military", 1)


@operation("2KIRK01", 1, uses=[A.PUT, A.DRAW_FROM_DISCARD], cost=[PutOnDeck(1)],
           requires=lambda ctx: any(is_suit(i, "Directive") for i in ctx.me.discard))
def orders(ctx, actions):
    """ACTIVATION: Put a card on the top of your deck to draw a Directive from your Discard pile."""
    yield from actions.draw_from_discard(lambda i: is_suit(i, "Directive"), "a Directive")


@endgame("2KIRK01")
def balanced(state, player):
    """ENDGAME: Score 1 [VP] for every second step gained on [Research]/[Influence]/[Military], whichever is the
    lowest. Ruling: current track positions, not multipliers."""
    return min(player.tracks.values()) // 2
