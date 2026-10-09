"""1SEL07 Scimitar (Ship, Development). Spec: resources/scans/base_game/cards/captains/sela/1SEL07.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import has_trait, location_of_player, others_in_hand, warp_this_ship

development_cost("1SEL07", Spend(dilithium=5))
REMUS = "1SEL19"


@operation("1SEL07", 0, uses=[A.FIND, A.DESTROY, A.BEAM, A.DEPLOY])
def unveil(ctx, actions):
    """PLAY: Find a Romulan and destroy the found card. Beam a card to Remus. If you do both, deploy this ship."""
    found, _ = yield from actions.find(lambda i: has_trait(i, "Romulan"), "a Romulan, to destroy it")
    if found is not None:
        yield from actions.destroy(found)
    remus = location_of_player(ctx.me, REMUS)
    beamed = None
    if remus is not None:
        beamed = yield from actions.pick_card("Beam which card to Remus?", others_in_hand(ctx))
        if beamed:
            yield from actions.beam(beamed, remus)
    if found is not None and beamed is not None:
        yield from actions.deploy(ctx.this_card)


operation("1SEL07", 1, uses=[A.WARP])(warp_this_ship)


@operation("1SEL07", 2, uses=[A.ATTACK, A.LOG, A.GAIN_RESOURCE, A.DISMISS],
           requires=lambda ctx: ctx.track("military") >= 7)
def thalaron_weapon(ctx, actions):
    """ATTACK ACTIVATION: Requires [Military] 7. Log an opponent Location. Gain 1 [Glory] for each Skill icon the
    logged card has. Dismiss this ship. The Cadet virtual opponent has one Location with one Skill icon
    (REQ-CTM-12)."""
    opp = ctx.opponent
    if (yield from actions.attack()):
        if opp is None:
            if ctx.virtual_opponent:
                yield from actions.gain_resource("glory", 1)
        elif opp.locations:
            loc = yield from actions.pick_card("Log which opponent Location?", list(opp.locations))
            icons = len(ctx.skills(loc, opp))
            yield from actions.log(loc)
            if icons:
                yield from actions.gain_resource("glory", icons)
    yield from actions.dismiss(ctx.this_card)


@operation("1SEL07", 3, uses=[A.TAKE_CONTROL],
           requires=lambda ctx: ctx.track("military") >= 9 and ctx.location_of(ctx.this_card) in ctx.state.neutral)
def occupy(ctx, actions):
    """ACTIVATION: Requires [Military] 9. Take control of this ship's (neutral) Location."""
    yield from actions.take_control(ctx.location_of(ctx.this_card))
