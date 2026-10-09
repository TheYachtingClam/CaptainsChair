"""1BUR24 Paul Stamets (Person). Spec: resources/scans/base_game/cards/captains/burnham/1BUR24.md"""

from engine.cards import operation
from engine.ops import A, EffectCost, Spend

from ._util import ships

DISCOVERY = "1BUR03"


@operation("1BUR24", 0, uses=[A.TAKE_INCIDENT, A.GAIN_SPECIALTY, A.MOVE_RESOURCES])
def mycelial_network(ctx, actions):
    """PLAY: You may take an Incident to gain 2 [Research]. For each deployed Ship you have in play, recrystallize 1
    [Dilithium]."""
    if (yield from actions.may("Take an Incident to gain 2 Research?")):
        yield from actions.take_incident()
        yield from actions.gain_specialty("research", 2)
    n = len(ships(ctx))
    if n:
        yield from actions.recrystallize(n)


def _discovery(ctx):
    return next((s for s in ctx.me.fleet if s.card == DISCOVERY), None)


def _dismiss_both(ctx, actions):
    yield from actions.dismiss(_discovery(ctx))
    yield from actions.dismiss(ctx.this_card)


@operation("1BUR24", 1, uses=[A.DISMISS, A.TAKE_ENCOUNTER],
           cost=[Spend(dilithium=3),
                 EffectCost(lambda ctx: _discovery(ctx) is not None, _dismiss_both, (A.DISMISS,),
                            "dismiss U.S.S. Discovery-A and this card")])
def the_jump(ctx, actions):
    """ACTIVATION: Dismiss U.S.S. Discovery-A and this card and spend 3 [Dilithium] to take the top Encounter."""
    yield from actions.take_encounter()
