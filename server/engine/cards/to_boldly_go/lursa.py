"""2PER10 Lursa (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER10.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import has_trait, ships


@operation("2PER10", 0, uses=[A.GAIN_RESOURCE, A.BEAM, A.SEND_AWAY_TEAM, A.SPEND, A.TAKE_INCIDENT, A.GAIN_CARD])
def duras_sister(ctx, actions):
    """PLAY: Gain 1 [Latinum]. You may beam this card to a Ship to send an [Away Team] to its Location. You may
    spend 1 [Dilithium] and take an Incident to gain a Ship."""
    yield from actions.gain_resource("latinum", 1)
    ship = yield from actions.pick_card("Beam Lursa to a Ship to send an Away Team to its Location?", ships(ctx),
                                        optional=True, none_label="No")
    if ship:
        yield from actions.beam(ctx.this_card, ship)
        loc = ctx.location_of(ship)
        if loc is not None:
            yield from actions.send_away_team(1, target=loc)
    if actions.can_spend(dilithium=1) and ctx.state.incident and (
            yield from actions.may("Spend 1 Dilithium and take an Incident to gain a Ship?")):
        yield from actions.spend(dilithium=1)
        yield from actions.take_incident()
        yield from actions.gain_card(["Ship"], label="a Ship")


@operation("2PER10", 1, uses=[A.DISCARD, A.DRAW, A.GAIN_SPECIALTY, A.GAIN_RESOURCE], cost=[DiscardFromHand(1)])
def deal(ctx, actions):
    """ACTIVATION: Discard a card to draw a card. If the discarded card is Romulan, gain 1 [Military]. If it is
    Business, gain 1 [Latinum]."""
    discarded = actions.paid[0]
    yield from actions.draw(1)
    if has_trait(discarded, "Romulan"):
        yield from actions.gain_specialty("military", 1)
    if has_trait(discarded, "Business"):
        yield from actions.gain_resource("latinum", 1)
