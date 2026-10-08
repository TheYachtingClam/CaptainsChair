"""Helpers shared with the base set. Registers nothing."""

from engine.cards.to_boldly_go._util import *  # noqa: F401,F403
from engine.cards.to_boldly_go._util import is_suit, others_in_hand


def draw_two_discard_one(ctx, actions):
    """Draw 2 cards and discard one of them: one of the cards just drawn."""
    before = list(ctx.me.hand)
    yield from actions.draw(2)
    drawn = [i for i in ctx.me.hand if i not in before]
    if drawn:
        yield from actions.discard(1, pred=lambda i: i in drawn, label="one of the drawn cards")


def incidents_in_hand(ctx):
    """Incidents you can return from your hand, without the card resolving now."""
    this = ctx.this_card
    return [i for i in ctx.hand_incidents() if i is not this]


def non_time_travel_in_staging(ctx):
    from engine.ops import trait_matches

    this = ctx.this_card
    return [i for i in ctx.me.staging if i is not this and not trait_matches(i, ("Time Travel",))]


def people_in_hand(ctx):
    return others_in_hand(ctx, lambda i: is_suit(i, "Person"))
