"""1SHR23 Andoria (Location). Spec: resources/scans/base_game/cards/captains/shran/1SHR23.md"""

from engine.cards import operation
from engine.ops import A

from ._util import away_team_draws, take_control_of_this

operation("1SHR23", 0, uses=[A.TAKE_CONTROL])(take_control_of_this)


@operation("1SHR23", 1, uses=[A.GAIN_SPECIALTY])
def homeworld(ctx, actions):
    """CONTROL: Gain 1 [Military] and 1 [Influence]."""
    yield from actions.gain_specialty("military", 1)
    yield from actions.gain_specialty("influence", 1)


operation("1SHR23", 2, uses=[A.DRAW])(away_team_draws)
