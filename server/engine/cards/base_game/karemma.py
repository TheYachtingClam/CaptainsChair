"""1ALL08 Karemma (Ally). Spec: resources/scans/base_game/cards/ally/1ALL08.md"""

from engine.cards import operation
from engine.ops import A, Spend


@operation("1ALL08", 0, uses=[A.GAIN_RESOURCE])
def trade(ctx, actions):
    """PLAY: Gain 1 [Latinum]."""
    yield from actions.gain_resource("latinum", 1)


@operation("1ALL08", 1, uses=[A.GAIN_ACTION], cost=[Spend(latinum=2)], requires=lambda ctx: ctx.track("military") >= 3)
def contract(ctx, actions):
    """PLAY: Requires [Military] 3. Spend 2 [Latinum] to gain an [Action]."""
    yield from actions.gain_action(1)
