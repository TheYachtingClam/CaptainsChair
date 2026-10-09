"""1LOC11 Freecloud (Location). Spec: resources/scans/base_game/cards/location/1LOC11.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import has_trait


@operation("1LOC11", 0, uses=[A.SPEND, A.SCAN_FOR])
def brokers(ctx, actions):
    """CONTROL: You may spend 1 [Latinum] to scan for Business."""
    if actions.can_spend(latinum=1) and (yield from actions.may("Spend 1 Latinum to scan for a Business?")):
        yield from actions.spend(latinum=1)
        yield from actions.scan_for(lambda i: has_trait(i, "Business"), "a Business")


@operation("1LOC11", 1, uses=[A.DISCARD, A.GAIN_RESOURCE], cost=[DiscardFromHand(1)])
def fence(ctx, actions):
    """ACTIVATION: Discard a card to gain 1 [Latinum]."""
    yield from actions.gain_resource("latinum", 1)


@operation("1LOC11", 2, uses=[A.FIND], cost=[Spend(latinum=2)])
def contacts(ctx, actions):
    """ACTIVATION: Spend 2 [Latinum] to find any card."""
    yield from actions.find(lambda i: True, "any card")
