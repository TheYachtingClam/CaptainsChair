"""2GEO02 U.S.S. Shenzhou (Ship). Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO02.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import is_suit


@operation("2GEO02", 0, uses=[A.DEPLOY, A.WARP, A.BEAM])
def deploy(ctx, actions):
    """PLAY: Deploy this ship. Warp this ship OR beam a card here."""
    ship = ctx.this_card
    yield from actions.deploy(ship)
    options = [("warp", "Warp this ship")] + ([("beam", "Beam a card here")] if ctx.me.hand else [])
    choice = yield from actions.choose("Warp the Shenzhou or beam a card to it?", options)
    if choice == "warp":
        yield from actions.warp(ship)
    else:
        card = yield from actions.pick_card("Beam which card?", list(ctx.me.hand))
        yield from actions.beam(card, ship)


@operation("2GEO02", 1, uses=[A.WARP], cost=[Spend(dilithium=1)])
def warp(ctx, actions):
    """ACTIVATION: Spend 1 Dilithium to warp this ship."""
    yield from actions.warp(ctx.this_card)


@operation("2GEO02", 2, uses=[A.BEAM], cost=[DiscardFromHand(1)], requires=lambda ctx: len(ctx.me.hand) >= 2)
def beam(ctx, actions):
    """ACTIVATION: Discard a card to beam a card here."""
    card = yield from actions.pick_card("Beam which card here?", list(ctx.me.hand))
    if card:
        yield from actions.beam(card, ctx.this_card)


@operation("2GEO02", 3, uses=[A.PROMOTE], requires=lambda ctx: any(is_suit(i, "Person") for i in ctx.me.hand))
def promote(ctx, actions):
    """ACTIVATION: Promote a Person from your hand to Duty Officer."""
    person = yield from actions.pick_card("Promote which Person?", [i for i in ctx.me.hand if is_suit(i, "Person")])
    yield from actions.promote(person)
