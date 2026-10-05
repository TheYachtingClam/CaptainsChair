"""2LOC07 Dozaria (Location). Spec: resources/scans/to_boldly_go/cards/location/2LOC07.md"""

from engine.cards import operation
from engine.ops import A


@operation("2LOC07", 0, uses=[A.GAIN_RESOURCE])
def mine(ctx, actions):
    """CONTROL: Gain 3 [Dilithium]."""
    yield from actions.gain_resource("dilithium", 3)
