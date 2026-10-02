"""2GEO20 Danby Connor (Person). Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO20.md"""

from engine.cards import operation
from engine.ops import A, LogFromHand

from ._util import has_trait, is_suit


@operation("2GEO20", 0, uses=[A.GAIN_SPECIALTY, A.LOG])
def military(ctx, actions):
    """PLAY: Gain 1 Military for each Person with Starfleet you have in play. If you gained 3 or more, log this card."""
    n = ctx.count_in_play(lambda i: is_suit(i, "Person") and has_trait(i, "Starfleet"))
    yield from actions.gain_specialty("military", n)
    if n >= 3:
        yield from actions.log(ctx.this_card)


@operation("2GEO20", 1, uses=[A.DRAW, A.GAIN_RESOURCE], cost=[LogFromHand()])
def log_for_reward(ctx, actions):
    """ACTIVATION: Log a card from your hand to either draw a card OR gain 2 Dilithium."""
    choice = yield from actions.choose("Draw a card or gain 2 Dilithium?", [("draw", "Draw a card"), ("dil", "Gain 2 Dilithium")])
    if choice == "draw":
        yield from actions.draw(1)
    else:
        yield from actions.gain_resource("dilithium", 2)
