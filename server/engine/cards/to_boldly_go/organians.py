"""2ALL08 Organians (Ally). Spec: resources/scans/to_boldly_go/cards/ally/2ALL08.md"""

from engine.cards import operation
from engine.ops import A


@operation("2ALL08", 0, uses=[A.ENLIST_RESERVE], requires=lambda ctx: ctx.track("research") >= 4)
def enlist_reserve(ctx, actions):
    """PLAY: Requires [Research] 4. Enlist a Reserve."""
    yield from actions.enlist_reserve()


@operation("2ALL08", 1, uses=[A.ENLIST_DEVELOPMENT, A.LOG], requires=lambda ctx: ctx.track("research") >= 6)
def enlist_development(ctx, actions):
    """PLAY: Requires [Research] 6. Enlist a Development and log this card."""
    yield from actions.enlist_development()
    yield from actions.log(ctx.this_card)
