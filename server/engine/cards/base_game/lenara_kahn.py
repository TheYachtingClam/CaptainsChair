"""1PER12 Lenara Kahn (Person). Spec: resources/scans/base_game/cards/person/1PER12.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import count_traits, has_trait


@operation("1PER12", 0, uses=[A.SPEND, A.GAIN_SPECIALTY, A.TAKE_INCIDENT, A.SCAN_FOR])
def experiment(ctx, actions):
    """PLAY: You may spend 1 [Dilithium] to gain 2 [Research]. You may take an Incident to scan for an Anomaly."""
    if actions.can_spend(dilithium=1) and (yield from actions.may("Spend 1 Dilithium to gain 2 Research?")):
        yield from actions.spend(dilithium=1)
        yield from actions.gain_specialty("research", 2)
    if ctx.state.incident and (yield from actions.may("Take an Incident to scan for an Anomaly?")):
        yield from actions.take_incident()
        yield from actions.scan_for(lambda i: has_trait(i, "Anomaly"), "an Anomaly")


@operation("1PER12", 1, uses=[A.GAIN_RESOURCE, A.DISMISS], cost=[Spend(latinum=1)])
def publish(ctx, actions):
    """ACTIVATION: Spend 1 [Latinum] to gain 1 [Glory] for each Anomaly you have in play (max 3). Dismiss this card."""
    n = min(3, count_traits(ctx, "Anomaly"))
    if n:
        yield from actions.gain_resource("glory", n)
    yield from actions.dismiss(ctx.this_card)
