"""1BUR10 Theta Zeta (Location, Development). Spec: resources/scans/base_game/cards/captains/burnham/1BUR10.md"""

from engine import cards as registry
from engine.cards import development_cost, endgame, operation
from engine.ops import A, Condition

from ._util import take_control_of_this

INERT_DILITHIUM = "1BUR02"

development_cost("1BUR10", Condition(lambda ctx: ctx.track("research") >= 12, "have 12+ Research"))

operation("1BUR10", 0, uses=[A.TAKE_CONTROL])(take_control_of_this)


@operation("1BUR10", 1, uses=[A.MOVE_RESOURCES, A.LOG, A.GAIN_RESOURCE])
def the_source(ctx, actions):
    """CONTROL: Recrystallize all [Dilithium]. Log Inert Dilithium (from play). Gain 4 [Glory]."""
    yield from actions.recrystallize()
    inert = next((i for i in ctx.me.status if i.card == INERT_DILITHIUM), None)
    if inert is not None:
        yield from actions.log(inert)
    yield from actions.gain_resource("glory", 4)


registry.NO_AWAY_TEAMS_HERE.add("1BUR10")  # PASSIVE: You cannot send [Away Team] here.


@endgame("1BUR10")
def reserves(state, player):
    """ENDGAME: Score 1 [VP] for every 2 [Dilithium] you have."""
    return player.dilithium // 2
