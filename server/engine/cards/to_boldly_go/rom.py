"""2PER17 Rom (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER17.md
"""

from engine.cards import operation
from engine.ops import A

from ._util import is_suit


@operation("2PER17", 0, uses=[A.SPEND, A.SCAN, A.FREE_PLAY])
def tinker(ctx, actions):
    """PLAY: You may spend 1 [Latinum] to scan 2 of Cargo. You may spend 1 [Latinum] to free play a Cargo from your
    hand or Discard pile."""
    if actions.can_spend(latinum=1) and (yield from actions.may("Spend 1 Latinum to scan 2 of Cargo?")):
        yield from actions.spend(latinum=1)
        yield from actions.scan(2, ["Cargo"])
    cargo = actions.free_play_candidates(lambda i: is_suit(i, "Cargo"), zones_=("hand", "discard"))
    if cargo and actions.can_spend(latinum=1):
        card = yield from actions.pick_card("Spend 1 Latinum to free play a Cargo from your hand or Discard pile?",
                                            cargo, optional=True, none_label="No")
        if card:
            yield from actions.spend(latinum=1)
            yield from actions.free_play(card)


@operation("2PER17", 1, uses=[A.DRAW, A.DRAW_FROM_DISCARD],
           trigger=lambda ctx, ev: ev["kind"] == "gain_resource" and ev["seat"] == ctx.me.seat
           and ev.get("resource") == "latinum")
def profit(ctx, actions):
    """REACTION: After gaining [Latinum], you may draw a card from your Draw deck and/or a card from your Discard
    pile."""
    if (yield from actions.may("Draw a card from your Draw deck?")):
        yield from actions.draw(1)
    if ctx.me.discard:
        yield from actions.draw_from_discard(optional=True)
