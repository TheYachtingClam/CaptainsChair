"""2SOV07 Minister Kuvak (Person, Development). Spec: resources/scans/to_boldly_go/cards/captains/soval/2SOV07.md"""

from engine.cards import development_cost, hand_size_modifier, operation
from engine.ops import A, Spend

from ._util import has_trait

development_cost("2SOV07", Spend(latinum=2))


@operation("2SOV07", 0, uses=[A.GAIN_RESOURCE])
def stipend(ctx, actions):
    """PLAY: Gain 1 [Dilithium] for each card you have beamed to a Ship/Location."""
    hosts = [*ctx.me.fleet, *ctx.me.locations]
    n = sum(len(h.beamed) for h in hosts)
    if n:
        yield from actions.gain_resource("dilithium", n)


@hand_size_modifier("2SOV07")
def diplomacy(state, owner, size):
    """PASSIVE: Increase your hand size by 1 for every non-Vulcan controlled Location you have in play (max 3)."""
    return size + min(3, sum(1 for loc in owner.locations if not has_trait(loc, "Vulcan")))
