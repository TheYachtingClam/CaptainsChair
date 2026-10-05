"""2LOC16 Solum (Location). Spec: resources/scans/to_boldly_go/cards/location/2LOC16.md"""

from engine.cards import operation
from engine.ops import A


@operation("2LOC16", 0, uses=[A.TAKE_INCIDENT])
def colony(ctx, actions):
    """CONTROL: Take an Incident to the bottom of your Draw deck."""
    yield from actions.take_incident(to="deck_bottom")
