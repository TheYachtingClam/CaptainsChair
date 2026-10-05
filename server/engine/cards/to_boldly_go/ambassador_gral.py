"""2PER02 Ambassador Gral (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER02.md
The attack PLAY and the Incident Reaction arrive in Step 4."""

from engine.cards import operation
from engine.ops import A


@operation("2PER02", 0, uses=[A.FIND])
def negotiate(ctx, actions):
    """PLAY: Find a card with [Influence]/[Influence Focus]."""
    yield from actions.find(lambda i: ctx.has_specialty_icon(i, "influence"), "a card with Influence")
