"""3PER04 Chef Riker (Person, Reward). Spec: resources/scans/second_contact/cards/rewards/3PER04.md"""

from engine import cards as registry
from engine.cards import operation
from engine.ops import A

from ._util import distinct_traits, has_trait, is_suit, minus_unless_logged

registry.VP_SPECIAL["3PER04"] = minus_unless_logged(1)  # SPECIAL: If not logged, this card scores -1.


@operation("3PER04", 0, uses=[A.DRAW_FROM_DISCARD, A.DUPLICATE, A.PROMOTE])
def galley(ctx, actions):
    """PLAY: Draw a card from your Discard pile for each different one of Beverage / Engineer / NX-01 you have in play.
    You may duplicate a play operation of a Person/Directive from your Log. You may promote this card to Duty Officer."""
    for _ in range(distinct_traits(ctx.in_play(), ("Beverage", "Engineer", "NX-01"))):
        if not ctx.me.discard:
            break
        yield from actions.draw_from_discard()
    logged = [i for i in ctx.me.log if is_suit(i, "Person", "Directive")]
    if logged:
        yield from actions.duplicate(logged, label="a Person or Directive in your Log")
    if ctx.this_card in ctx.me.staging and (yield from actions.may("Promote Chef Riker to Duty Officer?")):
        yield from actions.promote(ctx.this_card)


@operation("3PER04", 1, uses=[A.FREE_PLAY])
def shuttle_run(ctx, actions):
    """ACTIVATION: Free play a Ship with Starfleet."""
    cards = actions.free_play_candidates(lambda i: is_suit(i, "Ship") and has_trait(i, "Starfleet"))
    card = yield from actions.pick_card("Free play which Starfleet Ship?", cards)
    if card:
        yield from actions.free_play(card)


@operation("3PER04", 2, uses=[A.DRAW_FROM_DISCARD])
def leftovers(ctx, actions):
    """ACTIVATION: Draw a Ship/Hologram/NX-01 from your Discard pile."""
    yield from actions.draw_from_discard(lambda i: is_suit(i, "Ship") or has_trait(i, "Hologram", "NX-01"),
                                         "a Ship, Hologram or NX-01")
