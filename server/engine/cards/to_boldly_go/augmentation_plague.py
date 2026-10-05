"""2CAR01 Augmentation Plague (Cargo). Spec: resources/scans/to_boldly_go/cards/cargo/2CAR01.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import has_trait


@operation("2CAR01", 0, uses=[A.DEPLOY, A.GAIN_SPECIALTY, A.TAKE_INCIDENT, A.DRAW], cost=[Spend(dilithium=3, latinum=1)])
def outbreak(ctx, actions):
    """PLAY: Spend 3 [Dilithium] and 1 [Latinum] to deploy this card. Gain 2 [Military]. If your Captain is Klingon
    take an Incident to draw 3 cards. Ruling: the Klingon clause is mandatory."""
    yield from actions.deploy(ctx.this_card)
    yield from actions.gain_specialty("military", 2)
    if has_trait(ctx.me.captain, "Klingon"):
        yield from actions.take_incident()
        yield from actions.draw(3)


@operation("2CAR01", 2, uses=[A.GAIN_RESOURCE],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and has_trait(ctx.event_card, "Klingon"))
def klingon_glory(ctx, actions):
    """REACTION: After putting a Klingon into play, gain 1 [Glory]."""
    yield from actions.gain_resource("glory", 1)


@operation("2CAR01", 1, uses=[A.ATTACK, A.FORCE, A.DISCARD],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] != ctx.me.seat
           and ctx.event_card is not None and has_trait(ctx.event_card, "Klingon"))
def infect(ctx, actions):
    """ATTACK REACTION: After your opponent puts a Klingon into play force them to discard a card."""
    if (yield from actions.attack()) and ctx.opponent is not None:
        yield from actions.discard(1, player=ctx.opponent)
