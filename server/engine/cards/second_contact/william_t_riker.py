"""3RIK01 William T. Riker (Captain). Spec: resources/scans/second_contact/cards/captains/william riker/3RIK01.md"""

from engine.cards import operation
from engine.ops import A, PutOnDeck, TakeIncidentCost


def _can_swap(ctx):
    suits = {ctx.card(i).suit for i in ctx.me.discard}
    return any(ctx.card(i).suit in suits for i in ctx.me.hand)


@operation("3RIK01", 0, uses=[A.PUT, A.DRAW_FROM_DISCARD], cost=[PutOnDeck()], requires=_can_swap)
def swap(ctx, actions):
    """ACTIVATION: Put a card on the top of your deck to draw a card of the same suit from your Discard pile."""
    suit = ctx.card(actions.paid[0]).suit if actions.paid else None
    yield from actions.draw_from_discard(lambda i: ctx.card(i).suit == suit, f"a {suit}")


@operation("3RIK01", 1, uses=[A.TAKE_INCIDENT, A.SEND_AWAY_TEAM, A.SPEND, A.TRIGGER_CONTROL], cost=[TakeIncidentCost()])
def away_mission(ctx, actions):
    """ACTIVATION: Take an Incident to send an [Away Team] to a Location. If you targeted a controlled Location, you
    may spend 1 [Latinum] to trigger that card's control operation."""
    loc = yield from actions.send_away_team(1)
    if loc is not None and loc in ctx.me.locations and actions.can_spend(latinum=1) and (
            yield from actions.may(f"Spend 1 Latinum to trigger the CONTROL of {ctx.name(loc)}?")):
        yield from actions.spend(latinum=1)
        yield from actions.trigger_control(loc)
