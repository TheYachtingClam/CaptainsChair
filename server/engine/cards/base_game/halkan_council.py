"""1ALL07 Halkan Council (Ally). Spec: resources/scans/base_game/cards/ally/1ALL07.md"""

from engine.cards import operation
from engine.ops import A

from ._util import count_traits


@operation("1ALL07", 0, uses=[A.GAIN_RESOURCE])
def mines(ctx, actions):
    """PLAY: Gain 3 [Dilithium]."""
    yield from actions.gain_resource("dilithium", 3)


@operation("1ALL07", 1, uses=[A.LOG])
def pacifists(ctx, actions):
    """CLEAN-UP: If you have an Attack in play, log this card. Mandatory."""
    if count_traits(ctx, "Attack"):
        yield from actions.log(ctx.this_card)
