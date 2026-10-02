"""First Contact (Directive): 2GEO11, and the identical copy 2ARC14.
Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO11.md"""

from engine.cards import operation
from engine.ops import A


@operation(("2GEO11", "2ARC14"), 0, uses=[A.SCAN, A.LOG])
def scan_allies(ctx, actions):
    """PLAY: Scan 2 of Ally. Log this card."""
    yield from actions.scan(2, ["Ally"])
    yield from actions.log(ctx.this_card)
