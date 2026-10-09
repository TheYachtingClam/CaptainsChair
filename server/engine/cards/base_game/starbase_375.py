"""1SIS07 Starbase 375 (Location, Development). Spec: resources/scans/base_game/cards/captains/sisko/1SIS07.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import is_suit, take_control_of_this

development_cost("1SIS07", Spend(dilithium=4))
operation("1SIS07", 0, uses=[A.TAKE_CONTROL])(take_control_of_this)


@operation("1SIS07", 1, uses=[A.FIND])
def fleet_yards(ctx, actions):
    """CONTROL: You may find a Ship."""
    if (yield from actions.may("Find a Ship?")):
        yield from actions.find(lambda i: is_suit(i, "Ship"), "a Ship")


@operation("1SIS07", 2, uses=[A.FREE_PLAY],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and is_suit(ctx.event_card, "Ship")
           and any(is_suit(i, "Person") for i in ctx.me.hand))
def crew_assignment(ctx, actions):
    """REACTION: After putting a Ship into play, free play a Person."""
    person = yield from actions.pick_card("Free play which Person?",
                                          actions.free_play_candidates(lambda i: is_suit(i, "Person")))
    if person:
        yield from actions.free_play(person)
