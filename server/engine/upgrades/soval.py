"""Soval's Five-Year Mission upgrades. Spec: resources/scans/to_boldly_go/command/soval.md"""

from engine.ops import A
from engine.upgrades import boost
from engine.upgrades._shared import find_and_promote_person, gain_track_choice, is_suit

CREW = "soval"


@boost(CREW, "win", 0, uses=[A.GAIN_SPECIALTY])
def research_military_and_one(ctx, actions):
    """BOOST: Gain 1 [Research], 1 [Military], and 1 [Research]/[Military]."""
    yield from actions.gain_specialty("research", 1)
    yield from actions.gain_specialty("military", 1)
    yield from gain_track_choice(ctx, actions, 1, ("research", "military"))


@boost(CREW, "win", 1, moment="before_hand", uses=[A.FIND, A.PROMOTE])
def promote_a_person(ctx, actions):
    """BOOST: Before drawing the starting hand, find a Person, except in your Reserve deck, and promote them to Duty
    Officer."""
    yield from find_and_promote_person(ctx, actions)


@boost(CREW, "loss", 0, uses=[A.GAIN_SPECIALTY])
def research_or_military(ctx, actions):
    """BOOST: Gain 1 [Research]/[Military]."""
    yield from gain_track_choice(ctx, actions, 1, ("research", "military"))


@boost(CREW, "loss", 1, moment="after_hand", uses=[A.FIND])
def find_a_person(ctx, actions):
    """BOOST: After drawing the starting hand, find a Person in your Draw deck."""
    yield from actions.find(lambda i: is_suit(i, "Person"), "a Person", zones_=("draw",))
