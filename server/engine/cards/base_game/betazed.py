"""1LOC05 Betazed (Location). Spec: resources/scans/base_game/cards/location/1LOC05.md"""

from engine.cards import operation
from engine.ops import A


@operation("1LOC05", 0, uses=[A.GAIN_RESOURCE])
def hospitality(ctx, actions):
    """CONTROL: Gain 2 [Latinum]."""
    yield from actions.gain_resource("latinum", 2)
