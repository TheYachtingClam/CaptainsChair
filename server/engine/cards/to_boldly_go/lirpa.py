"""2CAR11 Lirpa (Cargo). Spec: resources/scans/to_boldly_go/cards/cargo/2CAR11.md"""

from engine.cards import operation
from engine.ops import A

from ._util import count_traits, others_in_hand


@operation("2CAR11", 0, uses=[A.ATTACK, A.FORCE, A.DISMISS, A.DRAW, A.PUT, A.GAIN_RESOURCE])
def kal_if_fee(ctx, actions):
    """ATTACK PLAY: Force your opponent to dismiss (one of) their Duty Officer(s). If they do, they may draw a card.
    You may put a card on the top of your deck to gain 1 [Glory]. Draw a card for each Vulcan you have in play
    (excluding this card, max 5). Ruling: the Vulcans are counted after the other steps."""
    opp = ctx.opponent
    if (yield from actions.attack()) and opp is not None and opp.duty:
        officer = yield from actions.pick_card("Lirpa: dismiss one of your Duty Officers.", list(opp.duty),
                                               seat=opp.seat)
        yield from actions.dismiss(officer)
        if (yield from actions.may("Draw a card?", seat=opp.seat)):
            yield from actions.draw(1, player=opp)
    card = yield from actions.pick_card("Put a card on top of your deck to gain 1 Glory?", others_in_hand(ctx),
                                        optional=True, none_label="No")
    if card:
        yield from actions.put_on_deck(card)
        yield from actions.gain_resource("glory", 1)
    vulcans = min(5, count_traits(ctx, "Vulcan", exclude=ctx.this_card))
    if vulcans:
        yield from actions.draw(vulcans)
