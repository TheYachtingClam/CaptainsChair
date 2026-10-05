"""2REB18 Samaritan Snare (Directive, Ongoing). Spec: resources/scans/to_boldly_go/cards/captains/rebner/2REB18.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, TakeIncidentCost

from ._util import is_suit
from .pakled_decree import HELMET_HERE


@operation("2REB18", 0, uses=[A.DEPLOY])
def deploy(ctx, actions):
    """PLAY: Deploy this card."""
    yield from actions.deploy(ctx.this_card)


@operation("2REB18", 1, uses=[A.BEAM, A.TAKE_INCIDENT, A.GAIN_CARD], cost=[HELMET_HERE, TakeIncidentCost()])
def lure(ctx, actions):
    """ACTIVATION: Beam a Helmet here, and take an Incident to gain a Ship / Ally."""
    yield from actions.gain_card(["Ship", "Ally"], label="a Ship or Ally")


@operation("2REB18", 2, uses=[A.DISCARD, A.GAIN_SPECIALTY],
           cost=[DiscardFromHand(1, lambda ctx, i: is_suit(i, "Incident"), "an Incident")])
def bluster(ctx, actions):
    """ACTIVATION: Discard an Incident to gain 1 [Military]."""
    yield from actions.gain_specialty("military", 1)
