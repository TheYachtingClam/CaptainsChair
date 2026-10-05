"""2ARC01 Jonathan Archer (Captain). Spec: resources/scans/to_boldly_go/cards/captains/archer/2ARC01.md"""

from engine.cards import endgame, operation
from engine.ops import A, card

from ._util import ctx_for, earth_of, ships


@operation("2ARC01", 0, uses=[A.EXHAUST, A.GAIN_RESOURCE])
def homeworld_support(ctx, actions):
    """RESUPPLY: If you have a deployed Ship and 3+ resources at Earth, you may exhaust this card to gain 3 resources
    from Earth."""
    earth = earth_of(ctx.me)
    if earth is None or not ships(ctx) or sum(earth.res.values()) < 3 or ctx.me.captain.exhausted:
        return
    if not (yield from actions.may("Exhaust Archer to gain 3 resources from Earth?")):
        return
    yield from actions.exhaust(ctx.me.captain)
    for n in (1, 2, 3):
        kinds = [k for k, v in sorted(earth.res.items()) if v]
        if not kinds:
            break
        kind = kinds[0] if len(kinds) == 1 else (
            yield from actions.choose(f"Take which resource from Earth ({n} of 3)?", [(k, k.capitalize()) for k in kinds]))
        yield from actions.gain_resource(kind, 1, source=earth)


@endgame("2ARC01")
def diversity(state, player):
    """ENDGAME: Score 1 [VP] for every 3 unique traits you have in play. Wildcard traits together count as one."""
    traits = set()
    for inst in ctx_for(state, player).in_play():
        traits |= set(card(inst).traits)
    return len(traits) // 3
