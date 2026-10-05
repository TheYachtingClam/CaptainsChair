"""2CAR06 Forced Singularity (Cargo). Spec: resources/scans/to_boldly_go/cards/cargo/2CAR06.md"""

from engine.cards import duty_slots, operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import has_trait, others_in_hand


@operation("2CAR06", 0, uses=[A.DISCARD, A.FIND, A.JUNK, A.DEPLOY], cost=[Spend(dilithium=2)])
def singularity(ctx, actions):
    """PLAY: You may discard a card to find an Engineer/Ops. Junk a card from the Market. Spend 2 [Dilithium] to
    deploy this card. Ruling: the 2 Dilithium is a required cost of the PLAY."""
    if others_in_hand(ctx) and (yield from actions.may("Discard a card to find an Engineer or Ops?")):
        yield from actions.discard(1)
        yield from actions.find(lambda i: has_trait(i, "Engineer", "Ops"), "an Engineer or Ops")
    yield from actions.junk()
    yield from actions.deploy(ctx.this_card)


@operation("2CAR06", 2, uses=[A.DRAW, A.PUT],
           cost=[DiscardFromHand(1, lambda ctx, i: has_trait(i, "Engineer"), "an Engineer")])
def engineering(ctx, actions):
    """ACTIVATION: Discard an Engineer to draw 2 cards and put one of them on the top of your deck."""
    before = list(ctx.me.hand)
    yield from actions.draw(2)
    drawn = [i for i in ctx.me.hand if i not in before]
    if drawn:
        card = yield from actions.pick_card("Put which drawn card on top of your deck?", drawn)
        yield from actions.put_on_deck(card)


@duty_slots("2CAR06")
def extra_officer(state, owner, inst):
    """PASSIVE: Requires [Military] 3. You may have an additional Person on duty."""
    return [None] if owner.tracks["military"] >= 3 else []
