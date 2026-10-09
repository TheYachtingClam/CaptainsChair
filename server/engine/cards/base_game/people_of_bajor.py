"""1SIS12 People of Bajor (Ally). Spec: resources/scans/base_game/cards/captains/sisko/1SIS12.md"""

from engine.cards import operation
from engine.ops import A, TakeIncidentCost


@operation("1SIS12", 0, uses=[A.TAKE_INCIDENT, A.GAIN_SPECIALTY, A.DRAW], cost=[TakeIncidentCost()])
def faith(ctx, actions):
    """PLAY: Take an Incident to gain 1 [Influence] and draw a card."""
    yield from actions.gain_specialty("influence", 1)
    yield from actions.draw(1)


@operation("1SIS12", 1, uses=[A.SEND_AWAY_TEAM, A.SPEND, A.LOG])
def militia(ctx, actions):
    """PLAY: Send an [Away Team] to a Location. You may spend 2 [Latinum] to send another [Away Team] to the same
    Location. Log this card."""
    loc = yield from actions.send_away_team(1)
    if loc is not None and actions.can_spend(latinum=2) and (
            yield from actions.may("Spend 2 Latinum to send another Away Team there?")):
        yield from actions.spend(latinum=2)
        yield from actions.send_away_team(1, target=loc)
    yield from actions.log(ctx.this_card)
