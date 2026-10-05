"""2CAR09 Jago's Epigenetic Implant (Cargo). Spec: resources/scans/to_boldly_go/cards/cargo/2CAR09.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import count_traits, has_trait, is_suit


@operation("2CAR09", 0, uses=[A.DEPLOY, A.GAIN_RESOURCE, A.FREE_PLAY], cost=[DiscardFromHand(1)])
def implant(ctx, actions):
    """PLAY: Discard a card to deploy this card. If the discarded card is Doctor or Business, gain 2 [Latinum] and
    you may free play an Incident."""
    yield from actions.deploy(ctx.this_card)
    if has_trait(actions.paid[0], "Doctor", "Business"):
        yield from actions.gain_resource("latinum", 2)
        incidents = actions.free_play_candidates(lambda i: is_suit(i, "Incident"))
        card = yield from actions.pick_card("Free play an Incident?", incidents, optional=True, none_label="No")
        if card:
            yield from actions.free_play(card)


@operation("2CAR09", 1, uses=[A.DRAW, A.DISCARD, A.DISMISS])
def augment(ctx, actions):
    """RESUPPLY: For each Augment you have in play: draw a card, then discard a card. If you have no Person on duty,
    dismiss this card."""
    for _ in range(count_traits(ctx, "Augment")):
        yield from actions.draw(1)
        yield from actions.discard(1)
    if not ctx.me.duty:
        yield from actions.dismiss(ctx.this_card)
