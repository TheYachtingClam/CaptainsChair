"""1SEL18 General Movar (Person). Spec: resources/scans/base_game/cards/captains/sela/1SEL18.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend, TakeIncidentCost

from ._util import count_traits, has_trait


def _attack(i):
    return has_trait(i, "Attack")


@operation("1SEL18", 0, uses=[A.DISCARD, A.SCAN_FOR],
           cost=[DiscardFromHand(1, lambda ctx, i: _attack(i), "an Attack"), Spend(dilithium=1)])
def collaborators(ctx, actions):
    """PLAY: Discard an Attack and spend 1 [Dilithium] to scan for a Shady."""
    yield from actions.scan_for(lambda i: has_trait(i, "Shady"), "a Shady")


@operation("1SEL18", 1, uses=[A.DRAW])
def network(ctx, actions):
    """RESUPPLY: Draw a card for every 2 Shady you have in play (max 4 cards)."""
    n = min(4, count_traits(ctx, "Shady") // 2)
    if n:
        yield from actions.draw(n)


@operation("1SEL18", 2, uses=[A.TAKE_INCIDENT, A.GAIN_RESOURCE, A.FREE_PLAY], cost=[TakeIncidentCost()])
def coup(ctx, actions):
    """ACTIVATION: Take an Incident to gain 1 [Dilithium]. If you do, you may free play an Attack."""
    yield from actions.gain_resource("dilithium", 1)
    attack = yield from actions.pick_card("Free play an Attack?", actions.free_play_candidates(_attack), optional=True,
                                          none_label="No")
    if attack:
        yield from actions.free_play(attack)
