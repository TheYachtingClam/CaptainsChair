"""2KIRK13 Pavel Chekov (Person). Spec: resources/scans/to_boldly_go/cards/captains/kirk/2KIRK13.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import is_suit


@operation("2KIRK13", 0, uses=[A.DISCARD, A.SEND_AWAY_TEAM, A.ATTACK, A.FORCE])
def landing_party(ctx, actions):
    """ATTACK PLAY: Discard the top card of your deck. Send an [Away Team] to a Location. If your opponent has at least
    one [Away Team] at the same Location, force them to discard a card."""
    yield from actions.discard_top()
    loc = yield from actions.send_away_team(1)
    opp = ctx.opponent
    if loc is not None and opp is not None and ctx.away_at(loc, opp) and (yield from actions.attack()):
        yield from actions.discard(1, player=opp)


@operation("2KIRK13", 1, uses=[A.DISCARD, A.SEND_AWAY_TEAM, A.GAIN_RESOURCE],
           cost=[DiscardFromHand(1, lambda ctx, i: is_suit(i, "Person"), "a Person")],
           trigger=lambda ctx, ev: ev["kind"] == "warp" and ev["seat"] == ctx.me.seat
           and any(l.uid == ev.get("location") for l in ctx.state.neutral))
def navigator(ctx, actions):
    """REACTION: After warping a Ship to a neutral Location, discard a Person to send an [Away Team] to the same
    Location, and gain 1 [Glory]."""
    loc = next((l for l in ctx.state.neutral if l.uid == ctx.event.get("location")), None)
    if loc is not None:
        yield from actions.send_away_team(1, target=loc)
    yield from actions.gain_resource("glory", 1)
