"""2REB13 Reginod (Person). Spec: resources/scans/to_boldly_go/cards/captains/rebner/2REB13.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_suit, others_in_hand, ships, wearing


@operation("2REB13", 0, uses=[A.DRAW_FROM_DISCARD, A.DISCARD, A.GAIN_RESOURCE, A.GAIN_SPECIALTY])
def tinker(ctx, actions):
    """PLAY: You may draw a Pakled from your Discard pile. You may discard a Cargo to gain 4 [Dilithium]. If the
    discarded card is Weapon, gain 1 [Military]."""
    yield from actions.draw_from_discard(lambda i: has_trait(i, "Pakled"), "a Pakled", optional=True)
    out = yield from actions.discard(1, pred=lambda i: is_suit(i, "Cargo"), label="a Cargo to gain 4 Dilithium",
                                     optional=True)
    if out:
        yield from actions.gain_resource("dilithium", 4)
        if has_trait(out[0], "Weapon"):
            yield from actions.gain_specialty("military", 1)


@operation("2REB13", 1, uses=[A.GAIN_RESOURCE])
def supply(ctx, actions):
    """RESUPPLY: Gain 1 [Dilithium]."""
    yield from actions.gain_resource("dilithium", 1)


@operation("2REB13", 2, uses=[A.DRAW_FROM_DISCARD, A.WARP, A.BEAM])
def engineer(ctx, actions):
    """ACTIVATION: If Reginod is wearing a Helmet, you may draw a Person from your Discard pile. Regardless: You may
    warp a Ship and you may beam a card to a Ship."""
    if wearing(ctx.this_card):
        yield from actions.draw_from_discard(lambda i: is_suit(i, "Person"), "a Person", optional=True)
    ship = yield from actions.pick_card("Warp a Ship?", ships(ctx), optional=True, none_label="No")
    if ship:
        yield from actions.warp(ship)
    if ships(ctx):
        card = yield from actions.pick_card("Beam a card to a Ship?", others_in_hand(ctx), optional=True,
                                            none_label="No")
        if card:
            ship = yield from actions.pick_card("To which Ship?", ships(ctx))
            yield from actions.beam(card, ship)
