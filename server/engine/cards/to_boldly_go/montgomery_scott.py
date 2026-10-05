"""2KIRK12 Montgomery "Scotty" Scott (Person). Spec: resources/scans/to_boldly_go/cards/captains/kirk/2KIRK12.md"""

from engine.cards import operation
from engine.ops import A, DismissFromPlay

from ._util import is_suit, ships


@operation("2KIRK12", 0, uses=[A.FIND, A.TAKE_INCIDENT])
def spare_parts(ctx, actions):
    """PLAY: Find a Ship. If the card was found in your Reserve deck, take an Incident."""
    _, zone = yield from actions.find(lambda i: is_suit(i, "Ship"), "a Ship")
    if zone == "reserve":
        yield from actions.take_incident()


@operation("2KIRK12", 1, uses=[A.DISMISS, A.TRIGGER_CONTROL, A.DRAW],
           cost=[DismissFromPlay(lambda ctx, i: i in ships(ctx), "one of your deployed Ships")],
           requires=lambda ctx: bool(ctx.me.locations))
def miracle_worker(ctx, actions):
    """PLAY: Dismiss a deployed Ship to trigger a controlled Location's control operation and draw a card."""
    loc = yield from actions.pick_card("Trigger the CONTROL of which Location?", list(ctx.me.locations))
    if loc:
        yield from actions.trigger_control(loc)
    yield from actions.draw(1)


@operation("2KIRK12", 2, uses=[A.GAIN_RESOURCE, A.REFRESH])
def engineering(ctx, actions):
    """ACTIVATION: Gain 2 [Dilithium]. Refresh a Ship/Cargo."""
    yield from actions.gain_resource("dilithium", 2)
    tired = [i for i in [*ctx.me.fleet, *ctx.me.staging] if i.exhausted and is_suit(i, "Ship", "Cargo")]
    card = yield from actions.pick_card("Refresh which Ship or Cargo?", tired)
    if card:
        yield from actions.refresh(card)
