"""1PIC06 Daystrom Institute (Location, Development). Spec: resources/scans/base_game/cards/captains/picard/1PIC06.md"""

from engine.cards import development_cost, endgame, operation
from engine.ops import A, Spend

from ._util import has_trait, owned_cards, take_control_of_this

development_cost("1PIC06", Spend(dilithium=3, latinum=1))
operation("1PIC06", 0, uses=[A.TAKE_CONTROL])(take_control_of_this)


def _synthetic(i):
    return has_trait(i, "Synthetic")


@operation("1PIC06", 1, uses=[A.SCAN_FOR])
def cybernetics(ctx, actions):
    """CONTROL: You may scan for a Synthetic."""
    if (yield from actions.may("Scan for a Synthetic?")):
        yield from actions.scan_for(_synthetic, "a Synthetic")


@operation("1PIC06", 2, uses=[A.FIND, A.GAIN_RESOURCE])
def archive(ctx, actions):
    """ACTIVATION: Find a Synthetic and gain 1 [Glory]."""
    yield from actions.find(_synthetic, "a Synthetic")
    yield from actions.gain_resource("glory", 1)


@operation("1PIC06", 3, uses=[A.DRAW])
def study(ctx, actions):
    """ACTIVATION: Draw a card."""
    yield from actions.draw(1)


@endgame("1PIC06")
def synthetics(state, player):
    """ENDGAME: Score 1 [VP] for each of your Synthetic cards."""
    return sum(1 for i in owned_cards(player) if _synthetic(i))
