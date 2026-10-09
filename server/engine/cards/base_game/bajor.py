"""1SIS02 Bajor (Location). Spec: resources/scans/base_game/cards/captains/sisko/1SIS02.md"""

from engine.cards import operation
from engine.ops import A

from ._util import away_team_draws

operation("1SIS02", 0, uses=[A.DRAW])(away_team_draws)
