"""2PER24 Travis Mayweather (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER24.md"""

from engine.cards import operation
from engine.ops import A, TakeIncidentCost

from ._util import ships


@operation("2PER24", 0, uses=[A.WARP, A.SPEND, A.SEND_AWAY_TEAM, A.EXHAUST], requires=lambda ctx: bool(ships(ctx)))
def helm(ctx, actions):
    """PLAY: Select a Ship and warp it. You may spend 2 [Dilithium] to send an [Away Team] to its Location. You may
    exhaust your Captain to send an [Away Team] to the same Location."""
    ship = yield from actions.pick_card("Warp which Ship?", ships(ctx))
    loc = yield from actions.warp(ship)
    if loc is None:
        return
    if actions.can_spend(dilithium=2) and (yield from actions.may(f"Spend 2 Dilithium to send an Away Team to {ctx.name(loc)}?")):
        yield from actions.spend(dilithium=2)
        yield from actions.send_away_team(1, target=loc)
    if not ctx.me.captain.exhausted and (
            yield from actions.may(f"Exhaust your Captain to send an Away Team to {ctx.name(loc)}?")):
        yield from actions.exhaust(ctx.me.captain)
        yield from actions.send_away_team(1, target=loc)


@operation("2PER24", 1, uses=[A.GAIN_ACTION, A.WARP], cost=[TakeIncidentCost()],
           trigger=lambda ctx, ev: ev["kind"] == "deploy" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and ctx.event_card in ships(ctx))
def full_impulse(ctx, actions):
    """REACTION: After deploying a Ship, take an Incident to gain an [Action], and you may warp the deployed Ship."""
    yield from actions.gain_action(1)
    ship = ctx.event_card
    if ship is not None and ship in ctx.me.fleet and (yield from actions.may(f"Warp {ctx.name(ship)}?")):
        yield from actions.warp(ship)
