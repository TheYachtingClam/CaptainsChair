"""Freeman's Five-Year Mission upgrades. Spec: resources/scans/second_contact/command/freeman.md"""

from engine.ops import A, TakeIncidentCost
from engine.upgrades import boost, own, reinforce
from engine.upgrades._shared import is_suit

CREW = "freeman"


@boost(CREW, "win", 0, moment="before_hand", uses=[A.SCAN_FOR], cost=[TakeIncidentCost()])
def scan_lower_decker(ctx, actions):
    """BOOST: Before drawing the starting hand, take an Incident to scan for Lower Decker."""
    yield from actions.scan_for(lambda i: ctx.has(i, "Lower Decker"), "a Lower Decker")


@boost(CREW, "win", 1, moment="after_hand", uses=[A.FIND, A.RETURN_INCIDENT])
def return_an_incident(ctx, actions):
    """BOOST: After drawing the starting hand, find an Incident and return it."""
    found, _ = yield from actions.find(lambda i: is_suit(i, "Incident"), "an Incident")
    if found is not None:
        yield from actions.return_incident(found)


@reinforce(CREW, "loss", 0)
def a_person(cards):
    """REINFORCE: A Person from your Available cards or Reserve deck."""
    return [own(cards, "Available", "Reserve", pred=lambda c: c.suit == "Person")]


@boost(CREW, "loss", 1, uses=[A.GAIN_ACTION])
def gain_an_action(ctx, actions):
    """BOOST: Gain an [Action]."""
    yield from actions.gain_action(1)
