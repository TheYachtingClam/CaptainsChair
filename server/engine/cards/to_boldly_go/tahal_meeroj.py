"""2LOC10 Tahal-Meeroj (Location). Spec: resources/scans/to_boldly_go/cards/location/2LOC10.md"""

from engine.cards import operation
from engine.ops import A


@operation("2LOC10", 0, uses=[A.ENLIST_RESERVE, A.DRAW])
def anomaly(ctx, actions):
    """CONTROL: You may enlist a Reserve. Draw 2 cards."""
    if ctx.me.reserve and (yield from actions.may("Enlist a Reserve?")):
        yield from actions.enlist_reserve()
    yield from actions.draw(2)


@operation("2LOC10", 1, uses=[A.GAIN_SPECIALTY],
           trigger=lambda ctx, ev: ev["kind"] == "log" and ev.get("uid") == ctx.ref.uid and ev.get("by") == ctx.me.seat)
def study(ctx, actions):
    """SPECIAL: When you log this card, gain 2 [Research]. It works from the Log, where the card now is."""
    yield from actions.gain_specialty("research", 2)
