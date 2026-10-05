"""2LOC05 Delta Vega (Location). Spec: resources/scans/to_boldly_go/cards/location/2LOC05.md"""

from engine.cards import operation
from engine.ops import A

from ._locations import no_effect
from ._util import is_suit

operation("2LOC05", 0, uses=[])(no_effect)


@operation("2LOC05", 1, uses=[A.REVEAL, A.GAIN_RESOURCE])
def outpost(ctx, actions):
    """RESUPPLY: Reveal your hand. For each Person in your hand, gain 1 [Dilithium]."""
    yield from actions.reveal(list(ctx.me.hand))
    people = sum(1 for i in ctx.me.hand if is_suit(i, "Person"))
    if people:
        yield from actions.gain_resource("dilithium", people)
