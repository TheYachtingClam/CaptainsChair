"""2PER07 Hoshi Sato (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER07.md
The Activation puts a card into the Staging Area, which arrives in Step 6."""

from engine.cards import operation
from engine.ops import SPECIES, A, DiscardFromHand

from ._util import has_trait


@operation("2PER07", 0, uses=[A.FIND])
def linguist(ctx, actions):
    """PLAY: Find a card with [Research]/[Research Focus]."""
    yield from actions.find(lambda i: ctx.has_specialty_icon(i, "research"), "a card with Research")


@operation("2PER07", 1, uses=[A.SCAN_FOR], requires=lambda ctx: ctx.track("research") >= 5,
           cost=[DiscardFromHand(1, lambda ctx, i: ctx.has_specialty_icon(i, "research"), "a card with Research")])
def first_contact(ctx, actions):
    """PLAY: Requires [Research] 5. Discard a card with [Research]/[Research Focus] to scan for Any Species of your
    choice."""
    species = yield from actions.choose("Scan for which Species?", [(s, s) for s in sorted(SPECIES)])
    yield from actions.scan_for(lambda i: has_trait(i, species), f"a {species}")
