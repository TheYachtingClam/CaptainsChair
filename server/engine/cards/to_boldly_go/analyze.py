"""Analyze (Directive): 2GEO15 and identical copies 2SOV17, 2ARC21, 2KIRK14, 3RIK19.
Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO15.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, TakeIncidentCost

IDS = ("2GEO15", "2SOV17", "2ARC21", "2KIRK14", "3RIK19")


@operation(IDS, 0, uses=[A.GAIN_CARD], cost=[TakeIncidentCost()])
def gain_ship(ctx, actions):
    """PLAY: Take an Incident to gain a Ship."""
    yield from actions.gain_card(["Ship"], label="a Ship")


@operation(IDS, 1, uses=[A.GAIN_CARD], cost=[DiscardFromHand(2)])
def gain_cargo(ctx, actions):
    """PLAY: Discard 2 cards to gain a Cargo."""
    yield from actions.gain_card(["Cargo"], label="a Cargo")


@operation(IDS, 2, uses=[A.GAIN_RESOURCE])
def dilithium(ctx, actions):
    """PLAY: Gain 2 Dilithium."""
    yield from actions.gain_resource("dilithium", 2)
