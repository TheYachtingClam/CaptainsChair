"""Shran's Five-Year Mission upgrades. Spec: resources/scans/base_game/command/shran.md"""

from engine.ops import A
from engine.upgrades import boost, own, reinforce
from engine.upgrades._shared import is_suit

CREW = "shran"


@boost(CREW, "win", 0, moment="before_hand", uses=[A.FIND, A.FREE_PLAY])
def free_play_a_location(ctx, actions):
    """BOOST: Before drawing the starting hand, find a Location (excluding from your Reserve deck) and immediately
    free play it."""
    found, _ = yield from actions.find(lambda i: is_suit(i, "Location"), "a Location", exclude_reserve=True)
    if found is not None:
        yield from actions.free_play(found)


@boost(CREW, "win", 1, uses=[A.GAIN_RESOURCE])
def two_dilithium(ctx, actions):
    """BOOST: Gain 2 [Dilithium]."""
    yield from actions.gain_resource("dilithium", 2)


@boost(CREW, "loss", 0, uses=[A.GAIN_RESOURCE])
def one_dilithium(ctx, actions):
    """BOOST: Gain 1 [Dilithium]."""
    yield from actions.gain_resource("dilithium", 1)


@reinforce(CREW, "loss", 1)
def a_reserve_card_loss(cards):
    """REINFORCE: A non-Incident card from your Reserve deck"""
    return [own(cards, "Reserve", pred=lambda c: c.suit != "Incident")]
