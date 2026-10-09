"""Helpers shared with the base set. Registers nothing."""

from engine.cards.to_boldly_go._util import *  # noqa: F401,F403
from engine.cards.to_boldly_go._locations import beamed_here, no_effect  # noqa: F401
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


def location_of_player(player, card_id: str):
    """A player's controlled Location with this id, for its ENDGAME."""
    return next((loc for loc in player.locations if loc.card == card_id), None)


def away_team_draws(ctx, actions):
    """ACTIVATION printed on many Crew Locations: "If you have an [Away Team] here, draw a card. If you have 3+ total
    [Away Team] on 1 or more controlled Location, draw a card."""
    n = int(ctx.away_at(ctx.this_card) > 0) + int(sum(ctx.away_at(loc) for loc in ctx.controlled_locations()) >= 3)
    if n:
        yield from actions.draw(n)
    else:
        actions.emit("No Away Team here and fewer than 3 on your Locations: no cards drawn.")


def take_control_of_this(ctx, actions):
    """PLAY: Take control of this location."""
    yield from actions.take_control(ctx.this_card)


def beamed_to_ships(ctx):
    """Your Ships, each with the cards on it: the Ship card and everything beamed to it (REQ-MS-03)."""
    from engine.cards.to_boldly_go._util import ships

    return [(ship, [ship, *ship.beamed]) for ship in ships(ctx)]
