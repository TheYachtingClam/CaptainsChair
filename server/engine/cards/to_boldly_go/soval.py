"""2SOV01 Soval (Captain). Spec: resources/scans/to_boldly_go/cards/captains/soval/2SOV01.md"""

from engine.cards import endgame, operation
from engine.ops import A, DismissFromPlay

from ._util import has_trait, is_suit, owned_cards


@operation("2SOV01", 0, uses=[A.DISMISS, A.DRAW],
           cost=[DismissFromPlay(lambda ctx, i: has_trait(i, "Human"), "a Human")])
def logic(ctx, actions):
    """ACTIVATION: Dismiss a Human to draw 2 cards. Ruling: the Human may be beamed, but not in the Staging Area."""
    yield from actions.draw(2)


@endgame("2SOV01")
def non_vulcans(state, player):
    """ENDGAME: Score 1 [VP] for each of your Person cards, excluding cards with Vulcan. Ruling: every Person you own,
    not only those in play."""
    return sum(1 for i in owned_cards(player) if is_suit(i, "Person") and not has_trait(i, "Vulcan"))
