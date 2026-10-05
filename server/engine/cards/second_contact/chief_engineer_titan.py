"""3RIK13 Chief Engineer (U.S.S. Titan) (Person). Spec: resources/scans/second_contact/cards/captains/william riker/3RIK13.md"""

from engine.cards import operation, trait_modifier
from engine.ops import A, DiscardFromHand, card

from ._util import has_trait, is_suit


@operation("3RIK13", 0, uses=[A.FIND, A.GAIN_RESOURCE])
def spare_ship(ctx, actions):
    """PLAY: Find a Ship and gain 1 [Dilithium]."""
    yield from actions.find(lambda i: is_suit(i, "Ship"), "a Ship")
    yield from actions.gain_resource("dilithium", 1)


@operation("3RIK13", 1, uses=[A.DISCARD, A.SCAN_FOR, A.DRAW],
           cost=[DiscardFromHand(1, lambda ctx, i: is_suit(i, "Ship"), "a Ship")])
def refit(ctx, actions):
    """PLAY: Discard a Ship to scan for a Weapon and draw a card."""
    yield from actions.scan_for(lambda i: has_trait(i, "Weapon"), "a Weapon")
    yield from actions.draw(1)


@trait_modifier("3RIK13")
def armed_crew(state, owner, inst, target):
    """PASSIVE: While this card is exhausted, all your other Person with Starfleet are additionally treated as
    Weapon."""
    if inst.exhausted and target is not inst and card(target).suit == "Person" and "Starfleet" in card(target).traits:
        return {"Weapon"}
    return set()


@operation("3RIK13", 3, uses=[A.DISCARD, A.GAIN_RESOURCE], cost=[DiscardFromHand(1)])
def jettison(ctx, actions):
    """ACTIVATION: Discard a card to discard the top card of your draw deck and gain 1 [Glory]."""
    yield from actions.discard_from_deck()
    yield from actions.gain_resource("glory", 1)
