"""3PIK26 Erica Ortegas (Person). Spec: resources/scans/second_contact/cards/captains/pike/3PIK26.md"""

from engine.cards import operation
from engine.ops import A, TakeIncidentCost

from ._util import is_suit, ships


@operation("3PIK26", 0, uses=[A.WARP, A.SPEND, A.SEND_AWAY_TEAM, A.TAKE_INCIDENT], requires=lambda ctx: bool(ships(ctx)))
def helm(ctx, actions):
    """PLAY: Select a Ship and warp it. You may spend 1 [Dilithium] to send an [Away Team] to its Location. You may
    take an Incident to send an [Away Team] to the same Location."""
    ship = yield from actions.pick_card("Warp which Ship?", ships(ctx))
    yield from actions.warp(ship)
    loc = ctx.location_of(ship)
    if loc is None:
        return
    if actions.can_spend(dilithium=1) and (yield from actions.may("Spend 1 Dilithium to send an Away Team there?")):
        yield from actions.spend(dilithium=1)
        yield from actions.send_away_team(1, target=loc)
    if TakeIncidentCost().can_pay(ctx) and (yield from actions.may("Take an Incident to send an Away Team there?")):
        yield from actions.take_incident()
        yield from actions.send_away_team(1, target=loc)


@operation("3PIK26", 1, uses=[A.WARP, A.GAIN_RESOURCE])
def joyride(ctx, actions):
    """RESUPPLY: You may warp a Ship to gain 1 [Dilithium]."""
    ship = yield from actions.pick_card("Warp a Ship to gain 1 Dilithium?", ships(ctx), optional=True, none_label="No")
    if ship:
        yield from actions.warp(ship)
        yield from actions.gain_resource("dilithium", 1)


@operation("3PIK26", 2, uses=[A.DISCARD, A.GAIN_RESOURCE, A.FIND],
           trigger=lambda ctx, ev: ev["kind"] == "deploy" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and is_suit(ctx.event_card, "Ship"))
def hit_it(ctx, actions):
    """REACTION: After deploying a Ship, you may discard a card to gain 1 [Glory], and you may discard a card to find
    Hit it."""
    if (yield from actions.discard(1, label="a card to gain 1 Glory", optional=True)):
        yield from actions.gain_resource("glory", 1)
    if (yield from actions.discard(1, label="a card to find Hit It", optional=True)):
        yield from actions.find(lambda i: i.card == "3PIK16", "Hit It", optional=True)
