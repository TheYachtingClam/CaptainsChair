"""2PER09 Landru (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER09.md
Landru has no PLAY. His second Activation takes control of the top Location, which arrives in Step 6."""

from engine.cards import operation
from engine.ops import A

from ._util import is_suit, others_in_hand


@operation("2PER09", 0, uses=[A.BEAM], requires=lambda ctx: bool(others_in_hand(ctx, lambda i: is_suit(i, "Person"))))
def absorb(ctx, actions):
    """ACTIVATION: Beam a Person here."""
    person = yield from actions.pick_card("Beam which Person to Landru?",
                                          others_in_hand(ctx, lambda i: is_suit(i, "Person")))
    yield from actions.beam(person, ctx.this_card)
