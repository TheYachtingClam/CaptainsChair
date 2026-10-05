"""2CAR15 Plasma Manifold (Cargo). Spec: resources/scans/to_boldly_go/cards/cargo/2CAR15.md"""

from engine.cards import operation
from engine.ops import A, Spend


@operation("2CAR15", 0, uses=[A.GAIN_ACTION], cost=[Spend(dilithium=3)])
def boost(ctx, actions):
    """PLAY: Spend 3 [Dilithium] to gain an [Action]."""
    yield from actions.gain_action(1)
