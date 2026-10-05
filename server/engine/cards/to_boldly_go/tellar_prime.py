"""2LOC18 Tellar Prime (Location). Spec: resources/scans/to_boldly_go/cards/location/2LOC18.md"""

from engine.cards import endgame, operation
from engine.ops import A, DiscardFromHand, PutOnDeck

from ._locations import no_effect
from ._util import has_trait, is_suit

operation("2LOC18", 0, uses=[])(no_effect)


@operation("2LOC18", 1, uses=[A.DISCARD, A.FIND], cost=[DiscardFromHand(1)])
def complaint(ctx, actions):
    """ACTIVATION: Discard a card to find an Incident."""
    yield from actions.find(lambda i: is_suit(i, "Incident"), "an Incident")


@operation("2LOC18", 2, uses=[A.PUT, A.SEND_AWAY_TEAM], cost=[PutOnDeck(1)])
def delegation(ctx, actions):
    """ACTIVATION: Put a card on the top of your deck to send an [Away Team] to a Location with Starfleet."""
    yield from actions.send_away_team(1, where=lambda loc: has_trait(loc, "Starfleet"))


@endgame("2LOC18")
def starbases(state, player):
    """ENDGAME: Score 1 [VP] for each controlled Location with Starfleet/Starbase you have in play."""
    return sum(1 for loc in player.locations if has_trait(loc, "Starfleet", "Starbase"))
