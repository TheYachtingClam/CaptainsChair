"""2ARC22 Strength of the Soul (Directive). Spec: resources/scans/to_boldly_go/cards/captains/archer/2ARC22.md"""

from engine.cards import operation
from engine.ops import A

from ._util import is_suit


@operation("2ARC22", 0, uses=[A.DRAW_FROM_DISCARD])
def resolve(ctx, actions):
    """PLAY: Draw a Directive/Encounter from your Discard pile."""
    yield from actions.draw_from_discard(lambda i: is_suit(i, "Directive", "Encounter"), "a Directive or Encounter")


@operation("2ARC22", 1, uses=[A.ENLIST_RESERVE, A.ENLIST_DEVELOPMENT, A.TAKE_INCIDENT, A.EXHAUST, A.DRAW])
def endure(ctx, actions):
    """PLAY: You may enlist a Reserve or a Development. You may take an Incident and exhaust your Captain to draw a card
    for every 2 controlled Location you have in play."""
    options = ([("reserve", "Enlist a Reserve")] if ctx.me.reserve else []) + \
        [("development", "Enlist a Development"), ("none", "Neither")]
    choice = yield from actions.choose("Enlist?", options)
    if choice == "reserve":
        yield from actions.enlist_reserve()
    elif choice == "development":
        yield from actions.enlist_development()
    n = len(ctx.me.locations) // 2
    if n and not ctx.me.captain.exhausted and ctx.state.incident and (
            yield from actions.may(f"Take an Incident and exhaust your Captain to draw {n}?")):
        yield from actions.take_incident()
        yield from actions.exhaust(ctx.me.captain)
        yield from actions.draw(n)
