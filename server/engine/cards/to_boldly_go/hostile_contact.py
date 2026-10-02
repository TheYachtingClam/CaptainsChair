"""Hostile Contact (Incident): 2GEO23 and identical copies 2INC02, 3RIK20.
Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO23.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import has_trait

IDS = ("2GEO23", "2INC02", "3RIK20")


@operation(IDS, 0, uses=[A.RETURN_INCIDENT, A.GAIN_RESOURCE], cost=[DiscardFromHand(1)])
def discard_to_return(ctx, actions):
    """PLAY: Discard a card to return this card. If the discarded card has Military/Military Focus, gain 2 Dilithium."""
    discarded = actions.paid[0]
    yield from actions.return_incident(ctx.this_card)
    if ctx.has_specialty_icon(discarded, "military"):
        yield from actions.gain_resource("dilithium", 2)


@operation(IDS, 1, uses=[A.RETURN_INCIDENT, A.GAIN_RESOURCE],
           requires=lambda ctx: ctx.count_in_play(lambda i: has_trait(i, "Communication")) > 0)
def communication(ctx, actions):
    """PLAY: If you have a Communication in play, return this card and gain 2 Dilithium."""
    yield from actions.return_incident(ctx.this_card)
    yield from actions.gain_resource("dilithium", 2)
