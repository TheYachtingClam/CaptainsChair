"""2LOC19 Verex III (Location). Spec: resources/scans/to_boldly_go/cards/location/2LOC19.md"""

from engine.cards import endgame, operation
from engine.ops import A, LogFromHand

from ._util import has_trait, is_suit, owned_cards


@operation("2LOC19", 0, uses=[A.GAIN_RESOURCE])
def syndicate(ctx, actions):
    """CONTROL: Gain 1 [Glory]."""
    yield from actions.gain_resource("glory", 1)


@operation("2LOC19", 1, uses=[A.LOG, A.GAIN_RESOURCE],
           cost=[LogFromHand(lambda ctx, i: is_suit(i, "Person"), "a Person")])
def trade(ctx, actions):
    """ACTIVATION: Log a Person to gain 2 [Latinum]."""
    yield from actions.gain_resource("latinum", 2)


@endgame("2LOC19")
def shady(state, player):
    """ENDGAME: Score 1 [VP] for each of your Shady cards."""
    return sum(1 for i in owned_cards(player) if has_trait(i, "Shady"))
