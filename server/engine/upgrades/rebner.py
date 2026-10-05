"""Rebner's Five-Year Mission upgrades. Spec: resources/scans/to_boldly_go/command/rebner.md"""

from engine.content import MARKET_SUITS
from engine.ops import A, TakeIncidentCost
from engine.upgrades import boost

CREW = "rebner"


@boost(CREW, "win", 0, moment="after_hand", uses=[A.DISCARD, A.DRAW])
def redraw_up_to_three(ctx, actions):
    """BOOST: After drawing the starting hand, discard up to 3 cards from your hand, then draw the same number of
    cards."""
    discarded = yield from actions.discard(3, optional=True)
    if discarded:
        yield from actions.draw(len(discarded))


@boost(CREW, "win", 1, moment="after_hand", uses=[A.GAIN_CARD])
def gain_from_deck_or_junk(ctx, actions):
    """BOOST: After drawing the starting hand, gain a card from the top of the deck or from the Junk."""
    yield from actions.gain_card(MARKET_SUITS, deck_only=True, from_junk=True, label="a card")


@boost(CREW, "loss", 0, moment="after_hand", uses=[A.SCAN], cost=[TakeIncidentCost()])
def scan_a_cargo(ctx, actions):
    """BOOST: After drawing the starting hand, take an Incident to scan 1 of Cargo."""
    yield from actions.scan(1, ["Cargo"])


@boost(CREW, "loss", 1, uses=[A.GAIN_RESOURCE])
def gain_a_latinum(ctx, actions):
    """BOOST: Gain 1 [Latinum]."""
    yield from actions.gain_resource("latinum", 1)
