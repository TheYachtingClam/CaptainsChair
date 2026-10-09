"""1SHR10 Jhamel (Person). Spec: resources/scans/base_game/cards/captains/shran/1SHR10.md"""

from engine.cards import operation
from engine.ops import A

from ._util import draw_then_decide, is_suit

operation("1SHR10", 0, uses=[A.DRAW, A.DISCARD, A.GAIN_RESOURCE, A.LOG])(draw_then_decide)


@operation("1SHR10", 1, uses=[A.FIND], trigger=lambda ctx, ev: ev["kind"] == "take_incident" and ev["seat"] == ctx.me.seat)
def sense(ctx, actions):
    """PASSIVE: After taking an Incident, you may find a Person."""
    if (yield from actions.may("Jhamel: find a Person?")):
        yield from actions.find(lambda i: is_suit(i, "Person"), "a Person")
