"""Georgiou's Five-Year Mission upgrades. Spec: resources/scans/to_boldly_go/command/georgiou.md"""

from engine.ops import A
from engine.upgrades import boost, own, reinforce

CREW = "georgiou"


def _person(c) -> bool:
    return c.suit == "Person"


@reinforce(CREW, "win", 0, each=True)
def a_person_from_each(cards):
    """REINFORCE: A Person from your Available cards and/or a Person from your Reserve deck."""
    return [own(cards, "Available", pred=_person), own(cards, "Reserve", pred=_person)]


@boost(CREW, "win", 1, moment="after_hand", uses=[A.DRAW, A.GAIN_ACTION])
def draw_and_action(ctx, actions):
    """BOOST: After drawing the starting hand, draw a card and gain an [Action]."""
    yield from actions.draw(1)
    yield from actions.gain_action(1)


@reinforce(CREW, "loss", 0)
def a_person(cards):
    """REINFORCE: A Person from your Available cards or Reserve deck."""
    return [own(cards, "Available", "Reserve", pred=_person)]


@boost(CREW, "loss", 1, uses=[A.GAIN_ACTION])
def gain_an_action(ctx, actions):
    """BOOST: Gain an [Action]."""
    yield from actions.gain_action(1)
