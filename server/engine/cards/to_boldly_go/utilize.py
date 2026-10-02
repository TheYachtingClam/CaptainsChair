"""Utilize (Directive): 2GEO18 and identical copies 2SOV23, 2KIRK19, and Riker's 3RIK08 (whose
development cost is not implemented yet). Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO18.md"""

from engine.cards import operation
from engine.ops import A

IDS = ("2GEO18", "2SOV23", "2KIRK19", "3RIK08")


@operation(IDS, 0, uses=[A.GAIN_RESOURCE])
def dilithium(ctx, actions):
    """PLAY: Gain 1 Dilithium, and 2 Dilithium for each controlled Location you have in play."""
    yield from actions.gain_resource("dilithium", 1 + 2 * len(ctx.me.locations))


@operation(IDS, 1, uses=[A.GAIN_SPECIALTY])
def specialty(ctx, actions):
    """PLAY: Gain on one Specialty track for each matching Skill icon you have in play (excluding beamed
    cards). Any Skill icons count for the chosen track."""
    cards = ctx.in_play(beamed=False)
    options = []
    for track in ("research", "influence", "military"):
        count = sum(1 for c in cards for s in ctx.skills(c) if s in (track.capitalize(), "Any"))
        options.append((track, f"{track.capitalize()}: +{count}", count))
    track = yield from actions.choose("Gain on which Specialty track?", [(t, label) for t, label, _ in options])
    count = next(n for t, _, n in options if t == track)
    yield from actions.gain_specialty(track, count)
