"""1BUR09 Earth (Location, Development). Spec: resources/scans/base_game/cards/captains/burnham/1BUR09.md  Not Archer's Earth (2ARC02)."""

from engine.cards import development_cost, operation
from engine.ops import A, Condition

from ._util import take_control_of_this

development_cost("1BUR09", Condition(lambda ctx: ctx.track("research") >= 8 and ctx.track("influence") >= 5,
                                     "have 8+ Research and 5+ Influence"))

operation("1BUR09", 0, uses=[A.TAKE_CONTROL])(take_control_of_this)


@operation("1BUR09", 1, uses=[A.GAIN_CARD])
def rejoin(ctx, actions):
    """CONTROL: You may gain a Person."""
    if (yield from actions.may("Gain a Person?")):
        yield from actions.gain_card(["Person"], label="a Person")


@operation("1BUR09", 2, uses=[A.GAIN_SPECIALTY])
def united_earth(ctx, actions):
    """ACTIVATION: Gain 1 [Influence] and 1 [Military]."""
    yield from actions.gain_specialty("influence", 1)
    yield from actions.gain_specialty("military", 1)
