"""Koloth's Five-Year Mission upgrades. Spec: resources/scans/base_game/command/koloth.md"""

from engine.ops import A
from engine.upgrades import boost, own, reinforce

CREW = "koloth"


@boost(CREW, "win", 0, uses=[A.GAIN_SPECIALTY])
def three_military(ctx, actions):
    """BOOST: Gain 3 [Military]."""
    yield from actions.gain_specialty("military", 3)


@boost(CREW, "win", 1, uses=[A.GAIN_RESOURCE])
def two_glory(ctx, actions):
    """BOOST: Gain 2 [Glory]."""
    yield from actions.gain_resource("glory", 2)


@reinforce(CREW, "loss", 0)
def a_reserve_card_loss(cards):
    """REINFORCE: A non-Incident card from your Reserve deck"""
    return [own(cards, "Reserve", pred=lambda c: c.suit != "Incident")]


@reinforce(CREW, "loss", 1)
def an_available_card_loss(cards):
    """REINFORCE: A non-Incident card from your Available cards."""
    return [own(cards, "Available", pred=lambda c: c.suit != "Incident")]
