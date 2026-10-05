"""2LOC11 Azati Prime (Location). Spec: resources/scans/to_boldly_go/cards/location/2LOC11.md"""

from engine.cards import endgame, operation
from engine.ops import A

from ._util import has_trait, others_in_hand, owned_cards


@operation("2LOC11", 0, uses=[A.PUT, A.GAIN_CARD, A.GAIN_RESOURCE])
def weapon_works(ctx, actions):
    """CONTROL: You may put a card on the top of your deck to gain a Cargo/Ship. If the gained card is Weapon, gain 2
    [Glory]."""
    if others_in_hand(ctx) and (yield from actions.may("Put a card on top of your deck to gain a Cargo or Ship?")):
        card = yield from actions.pick_card("Put which card on top of your deck?", others_in_hand(ctx))
        yield from actions.put_on_deck(card)
        gained = yield from actions.gain_card(["Cargo", "Ship"], label="a Cargo or Ship")
        if gained and has_trait(gained, "Weapon"):
            yield from actions.gain_resource("glory", 2)


@endgame("2LOC11")
def xindi(state, player):
    """ENDGAME: Score 1 [VP] for each of your Xindi cards."""
    return sum(1 for i in owned_cards(player) if has_trait(i, "Xindi"))
