"""2PER19 Soji Asha (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER19.md"""

from engine.cards import operation
from engine.ops import A, LogFromHand, Spend

from ._util import has_trait


@operation("2PER19", 0, uses=[A.SCAN_FOR], cost=[Spend(dilithium=2)])
def borg_artifacts(ctx, actions):
    """PLAY: Spend 2 [Dilithium] to scan for a Borg."""
    yield from actions.scan_for(lambda i: has_trait(i, "Borg"), "a Borg")


@operation("2PER19", 1, uses=[A.LOG, A.GAIN_RESOURCE], cost=[LogFromHand(zones=("discard",))])
def memories(ctx, actions):
    """PLAY: Log a card from your Discard pile to gain 1 [Dilithium]."""
    yield from actions.gain_resource("dilithium", 1)


@operation("2PER19", 2, uses=[A.LOG, A.DRAW], cost=[LogFromHand()],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and has_trait(ctx.event_card, "Synthetic"))
def awaken(ctx, actions):
    """REACTION: After putting a Synthetic into play (including this card), log a card from your hand to draw a card
    for every 5 cards in your Log."""
    n = len(ctx.me.log) // 5
    if n:
        yield from actions.draw(n)
