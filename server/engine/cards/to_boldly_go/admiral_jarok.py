"""2PER01 Admiral Jarok (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER01.md
The Reaction to attacks arrives in Step 4 and the PASSIVE (restriction and extra Duty Officer) in Step 5."""

from engine.cards import operation
from engine.ops import A


@operation("2PER01", 0, uses=[A.DRAW, A.ENLIST_DEVELOPMENT], requires=lambda ctx: ctx.track("military") >= 3)
def defect(ctx, actions):
    """PLAY: Requires [Military] 3. Your opponent may draw a card. Enlist a Development."""
    opp = ctx.opponent
    if opp is not None and (yield from actions.may("Admiral Jarok: do you want to draw a card?", seat=opp.seat)):
        yield from actions.draw(1, player=opp)
    yield from actions.enlist_development()
