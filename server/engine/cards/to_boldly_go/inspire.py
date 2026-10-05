"""2ARC15 Inspire (Directive). Spec: resources/scans/to_boldly_go/cards/captains/archer/2ARC15.md"""

from engine.cards import operation
from engine.ops import A


@operation("2ARC15", 0, uses=[A.DRAW, A.DISCARD, A.GAIN_SPECIALTY])
def inspire(ctx, actions):
    """PLAY: Draw 2 cards and discard one of the drawn cards. Gain on one Specialty track for each matching Skill icon
    you have in play (excluding beamed cards). Any Skill icons count for the chosen track."""
    before = list(ctx.me.hand)
    yield from actions.draw(2)
    drawn = [i for i in ctx.me.hand if i not in before]
    if drawn:
        yield from actions.discard(1, pred=lambda i: i in drawn, label="one of the drawn cards")
    cards = ctx.in_play(beamed=False)
    counts = {t: sum(1 for c in cards for s in ctx.skills(c) if s in (t.capitalize(), "Any"))
              for t in ("research", "influence", "military")}
    track = yield from actions.choose("Gain on which Specialty track?", [(t, f"{t.capitalize()}: +{n}")
                                                                         for t, n in counts.items()])
    yield from actions.gain_specialty(track, counts[track])
