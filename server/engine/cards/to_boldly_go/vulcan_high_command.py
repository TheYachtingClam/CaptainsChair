"""2SOV09 Vulcan High Command (Directive, Development). Spec: resources/scans/to_boldly_go/cards/captains/soval/2SOV09.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import has_trait

development_cost("2SOV09", Spend(dilithium=3))


@operation("2SOV09", 0, uses=[A.SEND_AWAY_TEAM, A.FIND])
def deployment(ctx, actions):
    """PLAY: Send an [Away Team] to a Location where you have a Ship. You may find a Vulcan."""
    yield from actions.send_away_team(1, where=lambda loc: bool(ctx.ships_at(loc)))
    if (yield from actions.may("Find a Vulcan?")):
        yield from actions.find(lambda i: has_trait(i, "Vulcan"), "a Vulcan", optional=True)


@operation("2SOV09", 1, uses=[A.SCAN_FOR, A.DRAW, A.LOG])
def liaison(ctx, actions):
    """PLAY: Scan for a Starfleet and draw 2 cards. Log this card."""
    yield from actions.scan_for(lambda i: has_trait(i, "Starfleet"), "a Starfleet")
    yield from actions.draw(2)
    yield from actions.log(ctx.this_card)
