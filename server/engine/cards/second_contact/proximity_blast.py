"""3RIK07 Proximity Blast (Directive, Development). Spec: resources/scans/second_contact/cards/captains/william riker/3RIK07.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import has_trait, ships

development_cost("3RIK07", Spend(dilithium=3))


def _targets(ctx):
    opp = ctx.opponent
    if opp is None:
        return []
    mine = {s.at for s in ships(ctx) if s.at}
    return [s for s in opp.fleet if s.at in mine]


@operation("3RIK07", 0, uses=[A.ATTACK, A.DISMISS, A.SPEND, A.DRAW, A.TAKE_INCIDENT])
def blast(ctx, actions):
    """ATTACK PLAY: Dismiss an opponent Ship sharing a Location with one of your Ship. You may spend 2 [Dilithium] to
    draw 2 cards. If you do, your opponent takes an Incident. Cadet: the virtual opponent's Ships are not at Locations
    (REQ-CTM-12), so there is nothing to dismiss."""
    if _targets(ctx) and (yield from actions.attack()):
        ship = yield from actions.pick_card("Dismiss which opponent Ship?", _targets(ctx))
        if ship:
            yield from actions.dismiss(ship)
    if actions.can_spend(dilithium=2) and (yield from actions.may("Spend 2 Dilithium to draw 2 cards?")):
        yield from actions.spend(dilithium=2)
        yield from actions.draw(2)
        yield from actions.take_incident(opponent=True)


def _armed_ships(ctx):
    neutral = {loc.uid for loc in ctx.state.neutral}
    return [s for s in ships(ctx) if s.at in neutral and sum(1 for b in s.beamed if has_trait(b, "Weapon")) >= 3]


@operation("3RIK07", 1, uses=[A.DISMISS, A.TAKE_CONTROL, A.LOG],
           requires=lambda ctx: ctx.track("influence") >= 5 and bool(_armed_ships(ctx)))
def overwhelm(ctx, actions):
    """PLAY: Requires [Influence] 5. Dismiss 3 Weapon beamed to the same Ship to take control of its neutral Location.
    Log this card."""
    ship = yield from actions.pick_card("Use the Weapons beamed to which Ship?", _armed_ships(ctx))
    loc = ctx.location_of(ship)
    for n in (1, 2, 3):
        weapon = yield from actions.pick_card(f"Dismiss which Weapon ({n} of 3)?",
                                              [b for b in ship.beamed if has_trait(b, "Weapon")])
        yield from actions.dismiss(weapon)
    yield from actions.take_control(loc)
    yield from actions.log(ctx.this_card)
