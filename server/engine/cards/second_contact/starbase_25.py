"""3RIK22 Starbase 25 (Location). Spec: resources/scans/second_contact/cards/captains/william riker/3RIK22.md"""

from engine.cards import operation
from engine.ops import A


@operation("3RIK22", 0, uses=[A.TAKE_CONTROL])
def take_control(ctx, actions):
    """PLAY: Take control of this location."""
    yield from actions.take_control(ctx.this_card)


@operation("3RIK22", 1, uses=[A.EXHAUST, A.GAIN_SPECIALTY, A.SPEND, A.SEND_AWAY_TEAM])
def dock(ctx, actions):
    """CONTROL: You may exhaust the U.S.S. Titan to gain 1 [Influence]. You may spend 1 [Dilithium] to send an [Away
    Team] here."""
    titan = next((s for s in ctx.me.fleet if s.card == "3RIK02" and not s.exhausted), None)
    if titan is not None and (yield from actions.may("Exhaust the U.S.S. Titan to gain 1 Influence?")):
        yield from actions.exhaust(titan)
        yield from actions.gain_specialty("influence", 1)
    if actions.can_spend(dilithium=1) and (yield from actions.may("Spend 1 Dilithium to send an Away Team here?")):
        yield from actions.spend(dilithium=1)
        yield from actions.send_away_team(1, target=ctx.this_card)


@operation("3RIK22", 2, uses=[A.DRAW])
def briefing(ctx, actions):
    """ACTIVATION: If you have an [Away Team] here, draw a card. If you have 3+ total [Away Team] on 1 or more
    controlled Location, draw a card."""
    n = (1 if ctx.away_at(ctx.this_card) else 0) + (1 if sum(ctx.away_at(loc) for loc in ctx.me.locations) >= 3 else 0)
    if n:
        yield from actions.draw(n)
    else:
        actions.emit("No Away Teams here: no cards drawn.")
