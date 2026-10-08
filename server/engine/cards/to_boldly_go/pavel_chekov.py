"""2KIRK13 Pavel Chekov (Person), and Khan's Cmdr. Chekov 2KHA07 (a Development) with the same operations.
Specs: resources/scans/to_boldly_go/cards/captains/kirk/2KIRK13.md and captains/kahn/2KHA07.md"""

from engine.cards import development_cost, operation
from engine.ops import A, DiscardFromHand, TakeIncidentCost

from ._util import is_suit

IDS = ("2KIRK13", "2KHA07")
development_cost("2KHA07", TakeIncidentCost())  # Cmdr. Chekov: Take an Incident.


@operation(IDS, 0, uses=[A.DISCARD, A.SEND_AWAY_TEAM, A.ATTACK, A.FORCE])
def landing_party(ctx, actions):
    """ATTACK PLAY: Discard the top card of your deck. Send an [Away Team] to a Location. If your opponent has at least
    one [Away Team] at the same Location, force them to discard a card."""
    yield from actions.discard_top()
    loc = yield from actions.send_away_team(1)
    opp = ctx.opponent
    if loc is not None and opp is not None and ctx.away_at(loc, opp) and (yield from actions.attack()):
        yield from actions.discard(1, player=opp)


def _warped_to_neutral(ctx, ev):
    return (ev["kind"] == "warp" and ev["seat"] == ctx.me.seat
            and any(l.uid == ev.get("location") for l in ctx.state.neutral))


_DISCARD_A_PERSON = [DiscardFromHand(1, lambda ctx, i: is_suit(i, "Person"), "a Person")]


@operation("2KIRK13", 1, uses=[A.DISCARD, A.SEND_AWAY_TEAM, A.GAIN_RESOURCE], cost=_DISCARD_A_PERSON,
           trigger=_warped_to_neutral)
def navigator(ctx, actions):
    """REACTION: After warping a Ship to a neutral Location, discard a Person to send an [Away Team] to the same
    Location, and gain 1 [Glory]."""
    loc = next((l for l in ctx.state.neutral if l.uid == ctx.event.get("location")), None)
    if loc is not None:
        yield from actions.send_away_team(1, target=loc)
    yield from actions.gain_resource("glory", 1)


@operation("2KHA07", 1, uses=[A.DISCARD, A.SEND_AWAY_TEAM, A.GAIN_RESOURCE], cost=_DISCARD_A_PERSON,
           trigger=_warped_to_neutral)
def controlled_navigator(ctx, actions):
    """REACTION: After warping a Ship to a neutral Location, discard a Person to send an [Away Team] to the same
    Location and gain 1 [Glory]. (Khan's Cmdr. Chekov; the same effect, printed without the comma.)"""
    yield from navigator(ctx, actions)
