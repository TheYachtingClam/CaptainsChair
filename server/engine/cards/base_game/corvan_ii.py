"""1LOC06 Corvan II (Location). Spec: resources/scans/base_game/cards/location/1LOC06.md"""

from engine.cards import operation
from engine.ops import A

from ._util import no_effect

operation("1LOC06", 0, uses=[])(no_effect)


@operation("1LOC06", 1, uses=[A.DISCARD, A.GAIN_RESOURCE])
def mining(ctx, actions):
    """RESUPPLY: Discard the top card of your deck. If the discarded card shares at least one trait with your Captain,
    gain 2 [Dilithium]. Otherwise, gain 1 [Dilithium]."""
    discarded = yield from actions.discard_from_deck()
    shared = discarded is not None and bool(ctx.traits(discarded) & ctx.traits(ctx.me.captain))
    yield from actions.gain_resource("dilithium", 2 if shared else 1)
