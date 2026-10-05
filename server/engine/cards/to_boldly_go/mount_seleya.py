"""2SOV04 Mount Seleya (Location, Development). Spec: resources/scans/to_boldly_go/cards/captains/soval/2SOV04.md"""

from engine.cards import development_cost, endgame, operation
from engine.ops import A, Condition, DiscardFromHand, Spend

from ._util import ctx_for, has_trait, is_suit

development_cost("2SOV04", Spend(dilithium=2),
                 Condition(lambda ctx: any(has_trait(i, "Vulcan") for i in ctx.me.log), "1+ Vulcan logged"))


@operation("2SOV04", 0, uses=[A.TAKE_CONTROL])
def take_control(ctx, actions):
    """PLAY: Take control of this location."""
    yield from actions.take_control(ctx.this_card)


@operation("2SOV04", 1, uses=[A.DRAW])
def katra(ctx, actions):
    """CONTROL: Draw a card for each Vulcan in your Log."""
    n = sum(1 for i in ctx.me.log if has_trait(i, "Vulcan"))
    if n:
        yield from actions.draw(n)


@operation("2SOV04", 2, uses=[A.DISCARD, A.FIND],
           cost=[DiscardFromHand(1, lambda ctx, i: is_suit(i, "Person"), "a Person")])
def meditation(ctx, actions):
    """ACTIVATION: Discard a Person to find any card."""
    yield from actions.find(lambda i: True, "any card")


@endgame("2SOV04")
def telepaths(state, player):
    """ENDGAME: Score 1 [VP] for each Telepath you have in play (including your Captain and beamed cards)."""
    return ctx_for(state, player).count_in_play(lambda i: has_trait(i, "Telepath"))
