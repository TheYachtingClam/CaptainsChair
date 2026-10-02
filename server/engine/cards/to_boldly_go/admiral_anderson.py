"""2GEO09 Admiral Anderson (Person). Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO09.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend, find_inst

from ._util import has_trait

development_cost("2GEO09", Spend(dilithium=4))


@operation("2GEO09", 0, uses=[A.ENLIST_DEVELOPMENT, A.DRAW])
def enlist_and_draw(ctx, actions):
    """PLAY: Enlist a Development and draw a card."""
    yield from actions.enlist_development()
    yield from actions.draw(1)


def _starfleet_put_into_play(ctx, ev):
    if ev["kind"] != "put_into_play" or ev["seat"] != ctx.me.seat:
        return False
    inst = find_inst(ctx.state, ev["uid"])
    return inst is not None and has_trait(inst, "Starfleet")


@operation("2GEO09", 1, uses=[A.DRAW], trigger=_starfleet_put_into_play)
def draw_on_starfleet(ctx, actions):
    """PASSIVE: After putting a Starfleet into play (including this card), you may draw a card."""
    if (yield from actions.may("Admiral Anderson: draw a card?")):
        yield from actions.draw(1)
