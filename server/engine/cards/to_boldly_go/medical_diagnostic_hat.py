"""2CAR12 Medical Diagnostic Hat (Cargo). Spec: resources/scans/to_boldly_go/cards/cargo/2CAR12.md"""

from engine.cards import operation
from engine.ops import A

from ._util import count_traits, is_suit


@operation("2CAR12", 0, uses=[A.DRAW, A.DRAW_FROM_DISCARD, A.FREE_PLAY])
def diagnose(ctx, actions):
    """PLAY: Draw a card for each Doctor/Alien you have in play (max 5 cards). You may draw a Person from your Discard
    pile. You may free play an Incident from your hand or Discard pile. Ruling: a card with both traits counts once."""
    n = min(5, count_traits(ctx, "Doctor", "Alien"))
    if n:
        yield from actions.draw(n)
    yield from actions.draw_from_discard(lambda i: is_suit(i, "Person"), "a Person", optional=True)
    incidents = actions.free_play_candidates(lambda i: is_suit(i, "Incident"), zones_=("hand", "discard"))
    card = yield from actions.pick_card("Free play an Incident from your hand or Discard pile?", incidents,
                                        optional=True, none_label="No")
    if card:
        yield from actions.free_play(card)
