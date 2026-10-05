"""2PER03 Ash Tyler (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER03.md
The attack PLAY arrives in Step 4."""

from engine.cards import hand_size_modifier, operation
from engine.ops import A

from ._util import count_traits


@operation("2PER03", 0, uses=[A.FIND],
           requires=lambda ctx: count_traits(ctx, "Starfleet", exclude=ctx.this_card)
           >= count_traits(ctx, "Klingon", exclude=ctx.this_card))
def starfleet_officer(ctx, actions):
    """PLAY: Requires Starfleet >= Klingon in play: Find a card with [Military]/[Military Focus].
    Ruling: Tyler counts himself for both traits, so he cancels out of the comparison."""
    yield from actions.find(lambda i: ctx.has_specialty_icon(i, "military"), "a card with Military")


@hand_size_modifier("2PER03")
def glory_hand_size(state, owner, size):
    """PASSIVE: If you have 8+ [Glory], increase your hand size by 2."""
    return size + 2 if owner.glory >= 8 else size
