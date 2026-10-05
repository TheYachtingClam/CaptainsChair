"""3PER06 Ensign Mariner (Person, Reward). Spec: resources/scans/second_contact/cards/rewards/3PER06.md"""

from engine import cards as registry
from engine.cards import operation
from engine.ops import A

from ._util import minus_unless_logged

registry.CANNOT_PROMOTE.add("3PER06")  # SPECIAL: This card cannot be promoted.
registry.VP_SPECIAL["3PER06"] = minus_unless_logged(1)  # SPECIAL: If not logged, this card scores -1.


@operation("3PER06", 0, uses=[A.GAIN_RESOURCE, A.TAKE_INCIDENT, A.FIND])
def rule_breaker(ctx, actions):
    """PLAY: Gain 1 [Latinum]. Up to twice: take an Incident to your Discard pile to find any card, except in your
    Reserve deck."""
    yield from actions.gain_resource("latinum", 1)
    for n in (1, 2):
        if not ctx.state.incident or not (
                yield from actions.may(f"Take an Incident to your Discard pile to find any card ({n} of up to 2)?")):
            break
        yield from actions.take_incident(to="discard")
        yield from actions.find(lambda i: True, "any card", exclude_reserve=True)


@operation("3PER06", 1, uses=[A.REFRESH, A.SEND_AWAY_TEAM],
           trigger=lambda ctx, ev: ev["kind"] == "exhaust" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and ctx.event_card in ctx.me.duty)
def covering(ctx, actions):
    """SUPPORT: After you exhaust a Duty Officer, refresh it and you may send an [Away Team] to a Location where you
    have a Ship."""
    yield from actions.refresh(ctx.event_card)
    if any(ctx.ships_at(loc) for loc in ctx.all_locations()) and (
            yield from actions.may("Send an Away Team to a Location where you have a Ship?")):
        yield from actions.send_away_team(1, where=lambda loc: bool(ctx.ships_at(loc)))
