"""1ENC01 Ancient Gene Fragments (Encounter). Spec: resources/scans/base_game/cards/encounter/1ENC01.md"""

from engine.cards import operation
from engine.ops import A

from ._util import count_traits


@operation("1ENC01", 0, uses=[A.DRAW, A.GAIN_ACTION])
def progenitors(ctx, actions):
    """PLAY: Draw a card for each controlled Location with 1+ [Away Team] you have. If you have a Scientist in play,
    gain an [Action]."""
    n = sum(1 for loc in ctx.controlled_locations() if ctx.away_at(loc) > 0)
    if n:
        yield from actions.draw(n)
    if count_traits(ctx, "Scientist"):
        yield from actions.gain_action(1)


@operation("1ENC01", 1, uses=[A.SCAN, A.DRAW])
def sequence(ctx, actions):
    """PLAY: Scan 2 of either Person, Cargo, Ship, or Ally. If you have a Scientist in play, draw a card."""
    yield from actions.scan(2, ["Person", "Cargo", "Ship", "Ally"])
    if count_traits(ctx, "Scientist"):
        yield from actions.draw(1)
