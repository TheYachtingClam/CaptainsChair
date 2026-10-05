"""2SOV10 Seleya (D'Kyr) (Ship). Spec: resources/scans/to_boldly_go/cards/captains/soval/2SOV10.md
Its first four operations are the D'Kyr Cruiser's (dkyr_cruiser.py)."""

from engine.cards import operation
from engine.ops import A

from ._util import is_suit, others_in_hand


@operation("2SOV10", 4, uses=[A.PROMOTE], requires=lambda ctx: bool(others_in_hand(ctx, lambda i: is_suit(i, "Person"))))
def bridge_officer(ctx, actions):
    """ACTIVATION: Promote a Person from your hand to Duty Officer."""
    person = yield from actions.pick_card("Promote which Person?", others_in_hand(ctx, lambda i: is_suit(i, "Person")))
    yield from actions.promote(person)
