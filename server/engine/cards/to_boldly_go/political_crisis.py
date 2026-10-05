"""2INC03 Political Crisis (Incident). Spec: resources/scans/to_boldly_go/cards/incident/2INC03.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import count_traits

IDS = ("2INC03", "3PIK14")  # Pike's Political Crisis is an identical copy


@operation(IDS, 0, uses=[A.DISCARD, A.RETURN_INCIDENT, A.GAIN_RESOURCE], cost=[DiscardFromHand(1)])
def negotiate(ctx, actions):
    """PLAY: Discard a card to return this card. If the discarded card has [Influence]/[Influence Focus], gain 1
    [Latinum]."""
    yield from actions.return_incident(ctx.this_card)
    if ctx.has_specialty_icon(actions.paid[0], "influence"):
        yield from actions.gain_resource("latinum", 1)


@operation(IDS, 1, uses=[A.RETURN_INCIDENT, A.GAIN_RESOURCE],
           requires=lambda ctx: count_traits(ctx, "Ambassador") > 0)
def diplomat(ctx, actions):
    """PLAY: If you have an Ambassador in play, return this card and gain 1 [Latinum]."""
    yield from actions.return_incident(ctx.this_card)
    yield from actions.gain_resource("latinum", 1)
