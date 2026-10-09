"""Picard's Five-Year Mission upgrades. Spec: resources/scans/base_game/command/picard.md"""

from engine.ops import A
from engine.upgrades import boost

CREW = "picard"


@boost(CREW, "win", 0, uses=[A.GAIN_SPECIALTY])
def three_research(ctx, actions):
    """BOOST: Gain 3 [Research]."""
    yield from actions.gain_specialty("research", 3)


@boost(CREW, "win", 1, moment="before_hand", uses=[A.FIND])
def find_two_cards(ctx, actions):
    """BOOST: Before drawing the starting hand, find two cards (excluding from your Reserve deck)."""
    for n in ("first", "second"):
        yield from actions.find(lambda i: True, f"any card (the {n} of two)", exclude_reserve=True)


@boost(CREW, "loss", 0, uses=[A.GAIN_SPECIALTY])
def one_research(ctx, actions):
    """BOOST: Gain 1 [Research]."""
    yield from actions.gain_specialty("research", 1)


@boost(CREW, "loss", 1, moment="before_hand", uses=[A.FIND])
def find_one_card(ctx, actions):
    """BOOST: Before drawing the starting hand, find one card (excluding from your Reserve deck)."""
    yield from actions.find(lambda i: True, "any card", exclude_reserve=True)
