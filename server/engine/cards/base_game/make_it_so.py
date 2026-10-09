"""1PIC03 Make It So (Directive, Development). Spec: resources/scans/base_game/cards/captains/picard/1PIC03.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

development_cost("1PIC03", Spend(dilithium=3))


def _secured(ctx):
    return [loc for loc in ctx.state.neutral if ctx.secured_by(loc)]


@operation("1PIC03", 0, uses=[A.RETURN_INCIDENT], requires=lambda ctx: bool(ctx.hand_incidents("discard")))
def resolve_it(ctx, actions):
    """PLAY: Return an Incident from your hand or Discard pile."""
    incident = yield from actions.pick_card("Return which Incident?", ctx.hand_incidents("discard"))
    yield from actions.return_incident(incident)


@operation("1PIC03", 1, uses=[A.TAKE_CONTROL, A.LOG],
           requires=lambda ctx: ctx.track("influence") >= 4 and bool(_secured(ctx)))
def engage(ctx, actions):
    """PLAY: Requires [Influence] 4. Select a secured neutral Location and take control of it. Log this card."""
    loc = yield from actions.pick_card("Take control of which secured Location?", _secured(ctx))
    yield from actions.take_control(loc)
    yield from actions.log(ctx.this_card)
