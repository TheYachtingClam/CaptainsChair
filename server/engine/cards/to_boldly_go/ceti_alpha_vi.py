"""2KHA03 Ceti Alpha VI (Location). Spec: resources/scans/to_boldly_go/cards/captains/kahn/2KHA03.md"""

from engine.cards import operation
from engine.ops import A, Spend, SpendFromHere, TakeIncidentCost


def _secured(ctx):
    return [loc for loc in ctx.state.neutral if ctx.secured_by(loc)]


@operation("2KHA03", 0, uses=[A.GAIN_RESOURCE, A.FLIP_CARD, A.TRIGGER_CONTROL, A.LOG])
def explode(ctx, actions):
    """RESUPPLY: If there are 4+ [Dilithium] here, gain all [Dilithium] here, flip Ceti Alpha V, and trigger Devastated
    Ceti Alpha V's control operation, then log this card. Ruling: this does not flip Khan's Captain."""
    here = ctx.this_card
    if here.res.get("dilithium", 0) < 4:
        return
    yield from actions.gain_resource("dilithium", here.res["dilithium"], source=here)
    home = next((loc for loc in ctx.me.locations if loc.card == "2KHA02A"), None)
    if home is not None:
        yield from actions.flip(home)
        yield from actions.trigger_control(home)
    yield from actions.log(here)


@operation("2KHA03", 1, uses=[A.GAIN_RESOURCE])
def mine(ctx, actions):
    """ACTIVATION: Gain 1 [Latinum]."""
    yield from actions.gain_resource("latinum", 1)


@operation("2KHA03", 2, uses=[A.TAKE_CONTROL],
           cost=[SpendFromHere(dilithium=1), Spend(latinum=1), TakeIncidentCost()],
           requires=lambda ctx: bool(_secured(ctx)))
def seize(ctx, actions):
    """ACTIVATION: Spend 1 [Dilithium] from this card, spend 1 [Latinum], and take an Incident to take control of a
    secured Location."""
    loc = yield from actions.pick_card("Take control of which secured Location?", _secured(ctx))
    if loc is not None:
        yield from actions.take_control(loc)


@operation("2KHA03", 3, uses=[A.PLACE_RESOURCES],
           trigger=lambda ctx, ev: ev["kind"] == "cycle" and ev["seat"] == ctx.me.seat)
def unstable_orbit(ctx, actions):
    """PASSIVE: After you cycle your deck, place 2 [Dilithium] here."""
    yield from actions.place_resources(ctx.this_card, "dilithium", 2)
