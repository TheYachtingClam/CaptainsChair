"""2SOV19 Infinite Diversity in Infinite Combinations (Directive).
Spec: resources/scans/to_boldly_go/cards/captains/soval/2SOV19.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_suit, ships


@operation("2SOV19", 0, uses=[A.REMOVE_AWAY_TEAM, A.LOG, A.DISMISS, A.TAKE_ENCOUNTER])
def idic(ctx, actions):
    """PLAY: You may remove an [Away Team] from a controlled Location, log a non-Vulcan Person/Cargo/Ally from your
    Staging Area, and dismiss a deployed Ship. If you do all three, look at the top 2 Encounter. Take one of them and
    put it on the top of your deck, and return the other to the bottom of its deck."""
    done = 0
    held = [loc for loc in ctx.me.locations if ctx.away_at(loc)]
    loc = yield from actions.pick_card("Remove an Away Team from a controlled Location?", held, optional=True,
                                       none_label="No")
    if loc:
        yield from actions.remove_away_team(loc, ctx.me)
        done += 1
    staged = [i for i in ctx.me.staging if is_suit(i, "Person", "Cargo", "Ally") and not has_trait(i, "Vulcan")
              and i is not ctx.this_card]
    card = yield from actions.pick_card("Log a non-Vulcan Person, Cargo or Ally from your Staging Area?", staged,
                                        optional=True, none_label="No")
    if card:
        yield from actions.log(card)
        done += 1
    ship = yield from actions.pick_card("Dismiss a deployed Ship?", ships(ctx), optional=True, none_label="No")
    if ship:
        yield from actions.dismiss(ship)
        done += 1
    if done == 3:
        yield from actions.take_encounter(look=2, to="top")
