"""1PIC04 Tamarians (Ally, Development). Spec: resources/scans/base_game/cards/captains/picard/1PIC04.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend, TakeIncidentCost

from ._util import is_suit, others_in_hand

development_cost("1PIC04", Spend(dilithium=2), TakeIncidentCost())
SUITS = ("Person", "Cargo", "Ship", "Ally", "Encounter", "Incident")


@operation("1PIC04", 0, uses=[A.DRAW, A.DISCARD, A.GAIN_RESOURCE, A.LOG])
def darmok(ctx, actions):
    """PLAY: Draw 3 cards. You may discard up to one of each of the following: Person, Cargo, Ship, Ally, Encounter,
    Incident. Gain 1 [Glory] for each card discarded this way. Log this card."""
    yield from actions.draw(3)
    left = list(SUITS)
    while left:
        cards = others_in_hand(ctx, lambda i: is_suit(i, *left))
        card = yield from actions.pick_card("Discard a card for 1 Glory (one of each suit)?", cards, optional=True,
                                            none_label="Stop")
        if not card:
            break
        suit = next(s for s in left if is_suit(card, s))
        left.remove(suit)
        yield from actions.discard(1, pred=lambda i: i.uid == card.uid)
        yield from actions.gain_resource("glory", 1)
    yield from actions.log(ctx.this_card)
