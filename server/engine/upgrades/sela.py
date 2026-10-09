"""Sela's Five-Year Mission upgrades. Spec: resources/scans/base_game/command/sela.md"""

from engine.ops import A
from engine.upgrades import boost, own, reinforce

CREW = "sela"


@boost(CREW, "win", 0, moment="before_hand", uses=[A.FIND, A.LOG])
def find_and_log(ctx, actions):
    """BOOST: Before drawing the starting hand, find a card (from your draw deck or Reserve) and log the found
    card."""
    found, _ = yield from actions.find(lambda i: True, "any card, to log it", zones_=("draw", "reserve"))
    if found is not None:
        yield from actions.log(found)


@boost(CREW, "win", 1, moment="after_hand", uses=[A.TAKE_FROM_REINFORCEMENT])
def take_a_reinforcement(ctx, actions):
    """BOOST: After drawing the starting hand, take a card from your Reinforcement deck."""
    yield from actions.take_from_reinforcement()


@reinforce(CREW, "loss", 0)
def a_reserve_card_loss(cards):
    """REINFORCE: A non-Incident card from your Reserve deck"""
    return [own(cards, "Reserve", pred=lambda c: c.suit != "Incident")]


@reinforce(CREW, "loss", 1)
def an_available_card_loss(cards):
    """REINFORCE: A non-Incident card from your Available cards."""
    return [own(cards, "Available", pred=lambda c: c.suit != "Incident")]
