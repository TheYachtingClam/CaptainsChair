"""2ARC10 Automated Repair Station (Location, Development). Spec: resources/scans/to_boldly_go/cards/captains/archer/2ARC10.md"""

from engine.cards import development_cost, operation
from engine.ops import A, LogFromHand

from ._util import is_suit

development_cost("2ARC10")  # no cost: it can be enlisted whenever enlisting a Development is allowed


@operation("2ARC10", 0, uses=[A.TAKE_CONTROL])
def take_control(ctx, actions):
    """PLAY: Take control of this location."""
    yield from actions.take_control(ctx.this_card)


@operation("2ARC10", 1, uses=[A.BEAM, A.SCAN])
def repairs(ctx, actions):
    """CONTROL: You may beam a Person here to scan 1 of Ship."""
    people = [i for i in ctx.me.hand if is_suit(i, "Person")]
    person = yield from actions.pick_card("Beam a Person here to scan 1 of Ship?", people, optional=True, none_label="No")
    if person:
        yield from actions.beam(person, ctx.this_card)
        yield from actions.scan(1, ["Ship"])


@operation("2ARC10", 2, uses=[A.DRAW], requires=lambda ctx: bool(ctx.ships_at(ctx.this_card)))
def docking(ctx, actions):
    """ACTIVATION: If you have a Ship here, draw a card."""
    yield from actions.draw(1)


@operation("2ARC10", 3, uses=[A.LOG, A.DRAW, A.GAIN_RESOURCE, A.REFRESH],
           cost=[LogFromHand(lambda ctx, i: is_suit(i, "Person"), "a Person", ("hand", "discard"))],
           trigger=lambda ctx, ev: ev["kind"] in ("deploy", "warp") and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and is_suit(ctx.event_card, "Ship"))
def overhaul(ctx, actions):
    """REACTION: After deploying or warping a Ship, log a Person from your hand or Discard pile to draw a card, gain 1
    [Dilithium], and refresh this card."""
    yield from actions.draw(1)
    yield from actions.gain_resource("dilithium", 1)
    yield from actions.refresh(ctx.this_card)
