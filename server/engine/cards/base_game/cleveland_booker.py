"""1BUR23 Cleveland Booker (Person). Spec: resources/scans/base_game/cards/captains/burnham/1BUR23.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import count_traits


@operation("1BUR23", 0, uses=[A.GAIN_RESOURCE])
def courier(ctx, actions):
    """PLAY: Gain 1 [Dilithium] and 1 [Latinum]."""
    yield from actions.gain_resource("dilithium", 1)
    yield from actions.gain_resource("latinum", 1)


@operation("1BUR23", 1, uses=[A.GAIN_CARD], cost=[Spend(dilithium=1)])
def contacts(ctx, actions):
    """PLAY: Spend 1 [Dilithium] to gain a Person or a Cargo."""
    yield from actions.gain_card(["Person", "Cargo"], label="a Person or a Cargo")


@operation("1BUR23", 2, uses=[A.DRAW, A.GAIN_RESOURCE], requires=lambda ctx: count_traits(ctx, "Creature") > 0)
def empathy(ctx, actions):
    """ACTIVATION: For each Creature you have in play either: draw a card OR gain 1 [Glory]."""
    n = count_traits(ctx, "Creature")
    for k in range(1, n + 1):
        choice = yield from actions.choose(f"Creature {k} of {n}:", [("draw", "Draw a card"), ("glory", "Gain 1 Glory")])
        if choice == "draw":
            yield from actions.draw(1)
        else:
            yield from actions.gain_resource("glory", 1)
