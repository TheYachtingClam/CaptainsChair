"""2KIRK09 Vulcan (Location, Development). Not Soval's starting Vulcan (2SOV03).
Spec: resources/scans/to_boldly_go/cards/captains/kirk/2KIRK09.md"""

from engine.cards import development_cost, endgame, operation
from engine.ops import A, Spend

from ._util import has_trait, highest_multiplier, is_suit

development_cost("2KIRK09", Spend(dilithium=4))


@operation("2KIRK09", 0, uses=[A.TAKE_CONTROL], requires=lambda ctx: ctx.track("research") >= 4)
def take_control(ctx, actions):
    """PLAY: Requires [Research] 4. Take control of this location."""
    yield from actions.take_control(ctx.this_card)


@operation("2KIRK09", 1, uses=[A.FIND, A.DRAW_FROM_DISCARD, A.FREE_PLAY])
def homeworld(ctx, actions):
    """CONTROL: You may find a Vulcan. You may draw Utilize from your Discard pile. You may free play an Incident."""
    if (yield from actions.may("Find a Vulcan?")):
        yield from actions.find(lambda i: has_trait(i, "Vulcan"), "a Vulcan", optional=True)
    if any(ctx.name(i) == "Utilize" for i in ctx.me.discard):
        yield from actions.draw_from_discard(lambda i: ctx.name(i) == "Utilize", "Utilize", optional=True)
    incidents = actions.free_play_candidates(lambda i: is_suit(i, "Incident"))
    card = yield from actions.pick_card("Free play an Incident?", incidents, optional=True, none_label="No")
    if card:
        yield from actions.free_play(card)


@endgame("2KIRK09")
def logic(state, player):
    """ENDGAME: Score [VP] equal to your highest multiplier on your Specialty tracks."""
    return highest_multiplier(player)
