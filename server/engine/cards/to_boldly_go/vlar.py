"""2SOV12 V'Lar (Person). Spec: resources/scans/to_boldly_go/cards/captains/soval/2SOV12.md"""

from engine.cards import operation
from engine.ops import A, Spend, TakeIncidentCost

from ._util import is_suit


@operation("2SOV12", 0, uses=[A.GAIN_CARD], cost=[Spend(latinum=1)])
def envoy(ctx, actions):
    """PLAY: Spend 1 [Latinum] to gain an Ally to your hand."""
    yield from actions.gain_card(["Ally"], label="an Ally", to_hand=True)


@operation("2SOV12", 1, uses=[A.TAKE_INCIDENT, A.DRAW, A.SEND_AWAY_TEAM], cost=[TakeIncidentCost()])
def mission(ctx, actions):
    """PLAY: Take an Incident to draw a card and send an [Away Team] to a Location where you have a Ship."""
    yield from actions.draw(1)
    yield from actions.send_away_team(1, where=lambda loc: bool(ctx.ships_at(loc)))


@operation("2SOV12", 2, uses=[A.DRAW, A.GAIN_RESOURCE],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and is_suit(ctx.event_card, "Ally"))
def alliance(ctx, actions):
    """REACTION: After putting an Ally into play, draw a card, gain 1 [Glory] and 1 [Latinum]."""
    yield from actions.draw(1)
    yield from actions.gain_resource("glory", 1)
    yield from actions.gain_resource("latinum", 1)
