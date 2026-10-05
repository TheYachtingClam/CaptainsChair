"""2PER05 Degra (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER05.md"""

from engine.cards import operation
from engine.ops import A, DismissFromPlay, Spend, TakeIncidentCost

from ._util import has_trait


@operation("2PER05", 0, uses=[A.SCAN_FOR, A.SPEND, A.DRAW], cost=[TakeIncidentCost()])
def research(ctx, actions):
    """PLAY: Take an Incident to scan for either an Anomaly or a Xindi. You may spend 1 [Dilithium] to draw 2 cards."""
    yield from actions.scan_for(lambda i: has_trait(i, "Anomaly", "Xindi"), "an Anomaly or a Xindi")
    if actions.can_spend(dilithium=1) and (yield from actions.may("Spend 1 Dilithium to draw 2 cards?")):
        yield from actions.spend(dilithium=1)
        yield from actions.draw(2)


@operation("2PER05", 1, uses=[A.TAKE_ENCOUNTER, A.LOG],
           cost=[DismissFromPlay(lambda ctx, i: has_trait(i, "Weapon"), "a Weapon"), Spend(dilithium=4)],
           requires=lambda ctx: ctx.track("research") >= 5)
def weapon_test(ctx, actions):
    """ACTIVATION: Requires [Research] 5. Dismiss a Weapon and spend 4 [Dilithium] to take the top Encounter. Log
    this card."""
    yield from actions.take_encounter()
    yield from actions.log(ctx.this_card)
