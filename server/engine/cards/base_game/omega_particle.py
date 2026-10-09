"""1ENC06 Omega Particle (Encounter). Spec: resources/scans/base_game/cards/encounter/1ENC06.md"""

from engine.cards import operation
from engine.ops import A

from ._util import count_traits


@operation("1ENC06", 0, uses=[A.GAIN_RESOURCE, A.DESTROY])
def perfection(ctx, actions):
    """PLAY: Gain 3 [Dilithium] and 3 [Latinum]. For each Borg you have in play gain 1 [Glory]. If you gained 5+
    [Glory] this way, destroy this card."""
    yield from actions.gain_resource("dilithium", 3)
    yield from actions.gain_resource("latinum", 3)
    borg = count_traits(ctx, "Borg")
    if borg:
        yield from actions.gain_resource("glory", borg)
    if borg >= 5:
        yield from actions.destroy(ctx.this_card)
