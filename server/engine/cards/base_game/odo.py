"""1SIS14 Odo (Person). Spec: resources/scans/base_game/cards/captains/sisko/1SIS14.md"""

from engine.cards import operation
from engine.ops import A, LogFromHand

from ._util import has_trait, is_suit


@operation("1SIS14", 0, uses=[A.DUPLICATE])
def shapeshift(ctx, actions):
    """PLAY: Duplicate a play operation of a Person or a Cargo from the Market."""
    market = [i for i in ctx.state.market.values() if i is not None and is_suit(i, "Person", "Cargo")]
    yield from actions.duplicate(market, label="a Person or Cargo in the Market", optional=False)


@operation("1SIS14", 1, uses=[A.LOG, A.DRAW, A.GAIN_RESOURCE],
           cost=[LogFromHand(lambda ctx, i: is_suit(i, "Person"), "a Person", zones=("hand", "discard"))])
def arrest(ctx, actions):
    """ACTIVATION: Log a Person from your hand or Discard pile to draw a card. If the logged card is Shady, gain 1
    [Glory]."""
    yield from actions.draw(1)
    if actions.paid and has_trait(actions.paid[0], "Shady"):
        yield from actions.gain_resource("glory", 1)
