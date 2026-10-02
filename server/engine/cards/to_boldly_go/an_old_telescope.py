"""2GEO07 An Old Telescope (Cargo, Ongoing). Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO07.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend, find_inst

from ._util import is_suit

development_cost("2GEO07", Spend(latinum=3))


@operation("2GEO07", 0, uses=[A.DEPLOY])
def deploy(ctx, actions):
    """PLAY: Deploy this card."""
    yield from actions.deploy(ctx.this_card)


@operation("2GEO07", 1, uses=[A.GAIN_RESOURCE],
           trigger=lambda ctx, ev: ev["kind"] == "gain_specialty" and ev["seat"] == ctx.me.seat and ev["track"] == "research")
def glory_on_research(ctx, actions):
    """REACTION: After gaining Research, gain 1 Glory."""
    yield from actions.gain_resource("glory", 1)


def _encounter_put_into_play(ctx, ev):
    if ev["kind"] != "put_into_play" or ev["seat"] != ctx.me.seat:
        return False
    inst = find_inst(ctx.state, ev["uid"])
    return inst is not None and is_suit(inst, "Encounter")


@operation("2GEO07", 2, uses=[A.DRAW], trigger=_encounter_put_into_play)
def draw_on_encounter(ctx, actions):
    """PASSIVE: After putting an Encounter into play, draw a card."""
    yield from actions.draw(1)
