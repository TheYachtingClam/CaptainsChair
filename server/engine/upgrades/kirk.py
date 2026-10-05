"""Kirk's Five-Year Mission upgrades. Spec: resources/scans/to_boldly_go/command/kirk.md"""

from engine.ops import A
from engine.upgrades import boost
from engine.upgrades._shared import gain_track_choice, is_suit

CREW = "kirk"


@boost(CREW, "win", 0, moment="before_hand", uses=[A.DISCARD, A.GAIN_SPECIALTY])
def discard_top_gain_two(ctx, actions):
    """BOOST: Before drawing the starting hand, discard the top card of your deck and gain 2
    [Research]/[Influence]/[Military]."""
    yield from actions.discard_from_deck()
    yield from gain_track_choice(ctx, actions, 2)


@boost(CREW, "win", 1, uses=[A.SEND_AWAY_TEAM])
def two_away_teams(ctx, actions):
    """BOOST: Send an [Away Team] each to two different neutral Location."""
    first = yield from actions.send_away_team(1, lambda loc: loc in ctx.state.neutral)
    if first is not None:
        yield from actions.send_away_team(1, lambda loc: loc in ctx.state.neutral and loc.uid != first.uid)


@boost(CREW, "loss", 0, uses=[A.GAIN_SPECIALTY])
def gain_one(ctx, actions):
    """BOOST: Gain 1 [Research]/[Influence]/[Military]."""
    yield from gain_track_choice(ctx, actions, 1)


@boost(CREW, "loss", 1, moment="after_hand", uses=[A.FIND])
def find_a_directive(ctx, actions):
    """BOOST: After drawing the starting hand, find a Directive in your Draw deck."""
    yield from actions.find(lambda i: is_suit(i, "Directive"), "a Directive", zones_=("draw",))
