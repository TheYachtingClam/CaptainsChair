"""3PIK11 Dak'Rah (Person). Spec: resources/scans/second_contact/cards/captains/pike/3PIK11.md"""

from engine.cards import operation
from engine.ops import A, TakeIncidentCost

from ._util import count_traits


@operation("3PIK11", 0, uses=[A.TAKE_INCIDENT, A.SCAN], cost=[TakeIncidentCost()])
def envoy(ctx, actions):
    """PLAY: Take an Incident to scan 1 of Ally."""
    yield from actions.scan(1, ["Ally"])


@operation("3PIK11", 1, uses=[A.GAIN_SPECIALTY])
def diplomacy(ctx, actions):
    """RESUPPLY: You may lose 1 [Military] to gain 3 [Influence]."""
    if ctx.track("military") >= 1 and (yield from actions.may("Lose 1 Military to gain 3 Influence?")):
        yield from actions.gain_specialty("military", -1)
        yield from actions.gain_specialty("influence", 3)


@operation("3PIK11", 2, uses=[A.LOG, A.GAIN_RESOURCE])
def honour(ctx, actions):
    """CLEAN-UP: If you have a Weapon in play, log this card and gain 1 [Glory]."""
    if count_traits(ctx, "Weapon"):
        yield from actions.log(ctx.this_card)
        yield from actions.gain_resource("glory", 1)
