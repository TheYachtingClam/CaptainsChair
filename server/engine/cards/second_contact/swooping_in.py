"""3RIK23 Swooping In (Directive). Spec: resources/scans/second_contact/cards/captains/william riker/3RIK23.md"""

from engine.cards import operation
from engine.ops import A

from ._util import ships


@operation("3RIK23", 0, uses=[A.WARP, A.GAIN_RESOURCE, A.GAIN_SPECIALTY])
def swoop(ctx, actions):
    """PLAY: Warp a Ship to a controlled Location, if able. Gain 1 [Dilithium], and 1 [Dilithium] for each controlled
    Location you have in play. If you have more [Research] than [Military] in play (excluding beamed cards), gain 1
    [Research]. Otherwise, gain 1 [Military]."""
    if ships(ctx) and ctx.me.locations:
        ship = yield from actions.pick_card("Warp which Ship to a controlled Location?", ships(ctx))
        yield from actions.warp(ship, destinations=list(ctx.me.locations))
    yield from actions.gain_resource("dilithium", 1 + len(ctx.me.locations))
    icons = [s for i in ctx.in_play(beamed=False) for s in ctx.skills(i)]
    track = "research" if icons.count("Research") > icons.count("Military") else "military"
    yield from actions.gain_specialty(track, 1)
