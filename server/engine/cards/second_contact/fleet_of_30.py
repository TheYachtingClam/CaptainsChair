"""3FRE03 A Fleet of 30 California-Class Ships (Ship, Development). Spec: resources/scans/second_contact/cards/captains/freeman/3FRE03.md"""

from engine import cards as registry
from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import ships

development_cost("3FRE03", Spend(dilithium=6))
registry.DUTY_LIMIT["3FRE03"] = 1  # PASSIVE: You may have an additional Person on duty.
registry.SHIP_WEIGHT["3FRE03"] = 2  # SPECIAL: counts as 2 tokens for securing (REQ-EXP-FRE-01, also for the Bot)


@operation("3FRE03", 0, uses=[A.DEPLOY, A.WARP, A.REFRESH])
def armada(ctx, actions):
    """PLAY: Deploy and warp this ship. Refresh every deployed Ship."""
    yield from actions.deploy(ctx.this_card)
    if ctx.this_card in ctx.me.fleet:
        yield from actions.warp(ctx.this_card)
    for ship in ships(ctx):
        if ship.exhausted:
            yield from actions.refresh(ship)
