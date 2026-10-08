"""1PER06 Bruce Maddox (Person). Spec: resources/scans/base_game/cards/person/1PER06.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait


@operation("1PER06", 0, uses=[A.FIND, A.FREE_PLAY])
def research(ctx, actions):
    """PLAY: Find and free play a Synthetic."""
    found, _ = yield from actions.find(lambda i: has_trait(i, "Synthetic"), "a Synthetic")
    if found is not None:
        yield from actions.free_play(found)


@operation("1PER06", 1, uses=[A.DRAW, A.GAIN_RESOURCE],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and ctx.has(ctx.event_card, "Android"))
def breakthrough(ctx, actions):
    """REACTION: After putting an Android into play, draw a card and gain 2 [Glory]."""
    yield from actions.draw(1)
    yield from actions.gain_resource("glory", 2)
