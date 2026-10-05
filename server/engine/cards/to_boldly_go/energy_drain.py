"""2SOV14 Energy Drain (Incident). Spec: resources/scans/to_boldly_go/cards/captains/soval/2SOV14.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import count_traits


@operation("2SOV14", 0, uses=[A.RETURN_INCIDENT, A.GAIN_ACTION], cost=[Spend(dilithium=2)])
def reroute_power(ctx, actions):
    """PLAY: Spend 2 [Dilithium] to return this card. If you have an Engineer in play, gain an [Action]."""
    yield from actions.return_incident(ctx.this_card)
    if count_traits(ctx, "Engineer"):
        yield from actions.gain_action(1)
