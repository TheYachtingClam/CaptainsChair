"""Burnham's Five-Year Mission upgrades. Spec: resources/scans/base_game/command/burnham.md"""

from engine.ops import A
from engine.upgrades import boost, own, reinforce

CREW = "burnham"


@boost(CREW, "win", 0, moment="after_hand", uses=[A.DRAW])
def draw_two(ctx, actions):
    """BOOST: After drawing the starting hand, draw 2 cards."""
    yield from actions.draw(2)


@reinforce(CREW, "win", 1)
def a_reserve_card_win(cards):
    """REINFORCE: A non-Incident card from your Reserve deck"""
    return [own(cards, "Reserve", pred=lambda c: c.suit != "Incident")]


@boost(CREW, "loss", 0, moment="after_hand", uses=[A.DRAW])
def draw_one(ctx, actions):
    """BOOST: After drawing the starting hand, draw 1 card."""
    yield from actions.draw(1)


@reinforce(CREW, "loss", 1)
def an_available_card_loss(cards):
    """REINFORCE: A non-Incident card from your Available cards."""
    return [own(cards, "Available", pred=lambda c: c.suit != "Incident")]
