"""1PIC21 Farpoint Station (Location). Spec: resources/scans/base_game/cards/captains/picard/1PIC21.md"""

from engine.cards import operation
from engine.ops import A

from ._util import away_team_draws, take_control_of_this

operation("1PIC21", 0, uses=[A.TAKE_CONTROL])(take_control_of_this)


@operation("1PIC21", 1, uses=[A.GAIN_SPECIALTY])
def mystery(ctx, actions):
    """CONTROL: Gain 1 [Research]."""
    yield from actions.gain_specialty("research", 1)


operation("1PIC21", 2, uses=[A.DRAW])(away_team_draws)
