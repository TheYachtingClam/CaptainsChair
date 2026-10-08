"""2KHA13 Marla McGivers (Person). Spec: resources/scans/to_boldly_go/cards/captains/kahn/2KHA13.md"""

from engine.cards import operation
from engine.ops import A

from ._util import count_traits, has_trait, others_in_hand


@operation("2KHA13", 0, uses=[A.GAIN_RESOURCE, A.PUT, A.PROMOTE])
def historian(ctx, actions):
    """PLAY: Gain 1 [Dilithium] for each Starfleet you have in play. Gain 1 [Dilithium] for each controlled Location
    you have in play. You may put 2 cards on the top of your deck to gain 1 [Glory] and promote this card to Duty
    Officer."""
    amount = count_traits(ctx, "Starfleet") + len(ctx.controlled_locations())
    if amount:
        yield from actions.gain_resource("dilithium", amount)
    if len(others_in_hand(ctx)) >= 2 and (yield from actions.may(
            "Put 2 cards on top of your deck to gain 1 Glory and promote Marla McGivers?")):
        for n in (1, 2):
            card = yield from actions.pick_card(f"Put which card on top of your deck ({n} of 2)?", others_in_hand(ctx))
            yield from actions.put_on_deck(card)
        yield from actions.gain_resource("glory", 1)
        yield from actions.promote(ctx.this_card)


@operation("2KHA13", 1, uses=[A.ENLIST_DEVELOPMENT, A.LOG])
def harsh_conditions(ctx, actions):
    """CLEAN-UP: If Devastated Ceti Alpha V is exhausted, enlist Ceti Eel for free then log this card."""
    if not any(loc.card == "2KHA02B" and loc.exhausted for loc in ctx.me.locations):
        return
    if any(i.card == "2KHA08" for i in ctx.me.development):
        yield from actions.enlist_development(free=True, pred=lambda i: i.card == "2KHA08")
    yield from actions.log(ctx.this_card)


@operation("2KHA13", 2, uses=[A.REFRESH, A.DISCARD, A.FIND])
def devotion(ctx, actions):
    """ACTIVATION: Refresh your Captain. You may discard a card to find an Augment."""
    yield from actions.refresh(ctx.me.captain)
    if others_in_hand(ctx) and (yield from actions.may("Discard a card to find an Augment?")):
        yield from actions.discard(1)
        yield from actions.find(lambda i: has_trait(i, "Augment"), "an Augment")
