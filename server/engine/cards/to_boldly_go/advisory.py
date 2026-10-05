"""2SOV20 Advisory (Directive). Spec: resources/scans/to_boldly_go/cards/captains/soval/2SOV20.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import has_trait, ships


@operation("2SOV20", 0, uses=[A.GAIN_SPECIALTY, A.DRAW, A.BEAM], cost=[Spend(dilithium=1)])
def counsel(ctx, actions):
    """PLAY: Spend 1 [Dilithium] to gain 1 [Influence] and draw a card. You may beam a Human to a deployed Ship.
    Rulebook example: beaming to an exhausted Ship is allowed."""
    yield from actions.gain_specialty("influence", 1)
    yield from actions.draw(1)
    humans = [i for i in ctx.me.hand if has_trait(i, "Human")]
    if humans and ships(ctx):
        human = yield from actions.pick_card("Beam a Human to a deployed Ship?", humans, optional=True, none_label="No")
        if human:
            ship = yield from actions.pick_card("To which Ship?", ships(ctx))
            yield from actions.beam(human, ship)


@operation("2SOV20", 1, uses=[A.SCAN, A.LOG])
def recruit_specialists(ctx, actions):
    """PLAY: Scan 2 of Person. Log this card."""
    yield from actions.scan(2, ["Person"])
    yield from actions.log(ctx.this_card)
