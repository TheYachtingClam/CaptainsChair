"""2KHA05 Surprise Attack (Directive, Development). Spec: resources/scans/to_boldly_go/cards/captains/kahn/2KHA05.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend, TakeIncidentCost

from ._util import has_trait

development_cost("2KHA05", Spend(dilithium=2), TakeIncidentCost())


@operation("2KHA05", 0, uses=[A.ATTACK, A.GIVE, A.RETURN_INCIDENT], cost=[Spend(dilithium=1)],
           requires=lambda ctx: bool(ctx.hand_incidents()))
def ambush(ctx, actions):
    """ATTACK PLAY: Spend 1 [Dilithium] to give your opponent an Incident (from your hand). If the attack is ignored,
    the Incident is returned instead (KW-GIVE-04)."""
    attacked = yield from actions.attack()
    incident = yield from actions.pick_card("Give which Incident?", ctx.hand_incidents())
    if attacked:
        yield from actions.give_incident(incident)
    elif incident is not None:
        yield from actions.return_incident(incident)


@operation("2KHA05", 1, uses=[A.SCAN_FOR, A.DRAW, A.DESTROY], cost=[Spend(dilithium=1)])
def scout(ctx, actions):
    """PLAY: Spend 1 [Dilithium] to scan for either a Cloak or a Spy, then draw a card. Destroy this card."""
    trait = yield from actions.choose("Scan for which trait?", [("Cloak", "Cloak"), ("Spy", "Spy")])
    yield from actions.scan_for(lambda i: has_trait(i, trait), f"a {trait}")
    yield from actions.draw(1)
    yield from actions.destroy(ctx.this_card)
