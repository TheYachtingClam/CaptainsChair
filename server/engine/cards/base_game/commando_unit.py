"""1SHR05 Commando Unit (Directive, Development). Spec: resources/scans/base_game/cards/captains/shran/1SHR05.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import has_trait, locations_with_your_ship

development_cost("1SHR05", Spend(dilithium=3))


def _weapon(i):
    return has_trait(i, "Weapon")


@operation("1SHR05", 0, uses=[A.SEND_AWAY_TEAM, A.FIND])
def insertion(ctx, actions):
    """PLAY: Send an [Away Team] to a Location where you have a Ship. You may find a Weapon."""
    if locations_with_your_ship(ctx):
        yield from actions.send_away_team(1, lambda loc: bool(ctx.ships_at(loc)))
    if (yield from actions.may("Find a Weapon?")):
        yield from actions.find(_weapon, "a Weapon")


@operation("1SHR05", 1, uses=[A.SCAN_FOR, A.DRAW])
def armoury(ctx, actions):
    """PLAY: Scan for a Weapon and draw a card."""
    yield from actions.scan_for(_weapon, "a Weapon")
    yield from actions.draw(1)
