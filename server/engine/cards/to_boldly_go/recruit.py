"""Recruit (Directive): 2GEO16 and identical copies 2SOV18, 2ARC20, 2KIRK18, 3RIK18.
Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO16.md"""

from engine.cards import operation
from engine.ops import A, PutOnDeck, TakeIncidentCost

IDS = ("2GEO16", "2SOV18", "2ARC20", "2KIRK18", "3RIK18")


@operation(IDS, 0, uses=[A.GAIN_CARD], cost=[PutOnDeck(1)])
def gain_person(ctx, actions):
    """PLAY: Put a card on the top of your deck to gain a Person."""
    yield from actions.gain_card(["Person"], label="a Person")


@operation(IDS, 1, uses=[A.GAIN_CARD], cost=[TakeIncidentCost()])
def gain_ally(ctx, actions):
    """PLAY: Take an Incident to gain an Ally."""
    yield from actions.gain_card(["Ally"], label="an Ally")
