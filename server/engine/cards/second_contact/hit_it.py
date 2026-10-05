"""3PIK16 Hit It (Directive). Spec: resources/scans/second_contact/cards/captains/pike/3PIK16.md"""

from engine.cards import operation
from engine.ops import A, TakeIncidentCost

from ._util import ships


def _enterprise_location(ctx):
    for ship in ctx.me.fleet:
        if ship.card == "3PIK19":
            loc = ctx.location_of(ship)
            if loc is not None and loc in ctx.me.locations:
                return loc
    return None


@operation("3PIK16", 0, uses=[A.DRAW, A.DISCARD, A.WARP])
def punch_it(ctx, actions):
    """PLAY: Draw 2 cards and discard one of the drawn cards. You may warp a Ship."""
    before = {i.uid for i in ctx.me.hand}
    yield from actions.draw(2)
    drawn = {i.uid for i in ctx.me.hand} - before
    if drawn:
        yield from actions.discard(1, pred=lambda i: i.uid in drawn, label="one of the drawn cards")
    ship = yield from actions.pick_card("Warp a Ship?", ships(ctx), optional=True, none_label="No")
    if ship:
        yield from actions.warp(ship)


@operation("3PIK16", 1, uses=[A.TAKE_INCIDENT, A.TRIGGER_CONTROL], cost=[TakeIncidentCost()],
           requires=lambda ctx: _enterprise_location(ctx) is not None)
def engage(ctx, actions):
    """PLAY: If the U.S.S. Enterprise is at a controlled Location, take an Incident to trigger that card's control
    operation."""
    yield from actions.trigger_control(_enterprise_location(ctx))
