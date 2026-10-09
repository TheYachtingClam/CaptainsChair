"""Sisko's Five-Year Mission upgrades. Spec: resources/scans/base_game/command/sisko.md"""

from engine.ops import A
from engine.upgrades import boost

CREW = "sisko"


@boost(CREW, "win", 0, uses=[A.GAIN_SPECIALTY])
def three_influence(ctx, actions):
    """BOOST: Gain 3 [Influence]."""
    yield from actions.gain_specialty("influence", 3)


@boost(CREW, "win", 1, uses=[A.GAIN_RESOURCE])
def two_latinum(ctx, actions):
    """BOOST: Gain 2 [Latinum]."""
    yield from actions.gain_resource("latinum", 2)


@boost(CREW, "loss", 0, uses=[A.GAIN_SPECIALTY])
def one_influence(ctx, actions):
    """BOOST: Gain 1 [Influence]."""
    yield from actions.gain_specialty("influence", 1)


@boost(CREW, "loss", 1, uses=[A.GAIN_RESOURCE])
def one_dilithium(ctx, actions):
    """BOOST: Gain 1 [Dilithium]."""
    yield from actions.gain_resource("dilithium", 1)
