"""1SEL20 Romulus (Location). Spec: resources/scans/base_game/cards/captains/sela/1SEL20.md"""

from engine.cards import operation
from engine.ops import A

from ._util import away_team_draws, is_suit, take_control_of_this

operation("1SEL20", 0, uses=[A.TAKE_CONTROL])(take_control_of_this)


@operation("1SEL20", 1, uses=[A.FREE_PLAY])
def shipyards(ctx, actions):
    """CONTROL: You may free play a Ship."""
    ship = yield from actions.pick_card("Free play a Ship?", actions.free_play_candidates(lambda i: is_suit(i, "Ship")),
                                        optional=True, none_label="No")
    if ship:
        yield from actions.free_play(ship)


operation("1SEL20", 2, uses=[A.DRAW])(away_team_draws)
