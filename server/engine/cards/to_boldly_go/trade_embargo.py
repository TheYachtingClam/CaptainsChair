"""2INC06 Trade Embargo (Incident). Spec: resources/scans/to_boldly_go/cards/incident/2INC06.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import ships


@operation("2INC06", 0, uses=[A.RETURN_INCIDENT, A.REFRESH], cost=[Spend(latinum=1)])
def lift_embargo(ctx, actions):
    """PLAY: Spend 1 [Latinum] to return this card. You may refresh a Ship."""
    yield from actions.return_incident(ctx.this_card)
    tired = [s for s in ships(ctx) if s.exhausted]
    ship = yield from actions.pick_card("Refresh a Ship?", tired, optional=True, none_label="No")
    if ship:
        yield from actions.refresh(ship)
