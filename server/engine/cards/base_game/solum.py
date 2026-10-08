"""1LOC17 Solum (Location), the older Core Box version. Spec: resources/scans/base_game/cards/location/1LOC17.md
It plays as To Boldly Go's version (2LOC16) does; only the wording and its trait differ."""

from engine.cards import operation
from engine.ops import A


@operation("1LOC17", 0, uses=[A.TAKE_INCIDENT])
def colony(ctx, actions):
    """CONTROL: Take an Incident and put it on the bottom of your Draw deck."""
    yield from actions.take_incident(to="deck_bottom")
