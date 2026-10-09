"""1SEL16 Sub-Commander T'Rul (Person). Spec: resources/scans/base_game/cards/captains/sela/1SEL16.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, others_in_hand


def _cloak(i):
    return has_trait(i, "Cloak")


@operation("1SEL16", 0, uses=[A.DRAW, A.DISCARD, A.DRAW_FROM_DISCARD])
def engineer(ctx, actions):
    """PLAY: Draw a card. You may discard a card to draw a Cloak from your Discard pile."""
    yield from actions.draw(1)
    if others_in_hand(ctx) and any(_cloak(i) for i in ctx.me.discard) and (
            yield from actions.may("Discard a card to draw a Cloak from your Discard pile?")):
        discarded = yield from actions.discard(1)
        gone = discarded[0].uid if discarded else None
        yield from actions.draw_from_discard(lambda i: _cloak(i) and i.uid != gone, "a Cloak")


@operation("1SEL16", 1, uses=[A.GAIN_RESOURCE],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and ctx.has(ctx.event_card, "Cloak"))
def installation(ctx, actions):
    """REACTION: After putting a Cloak into play, gain 1 [Latinum]."""
    yield from actions.gain_resource("latinum", 1)
