"""2LOC08 Indri VIII (Location). Spec: resources/scans/to_boldly_go/cards/location/2LOC08.md"""

from engine.cards import operation
from engine.ops import A


@operation("2LOC08", 0, uses=[A.GAIN_ACTION])
def discovery(ctx, actions):
    """CONTROL: Gain an [Action]."""
    yield from actions.gain_action(1)
