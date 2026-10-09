"""1SIS01 Benjamin Sisko (Captain). Spec: resources/scans/base_game/cards/captains/sisko/1SIS01.md"""

from engine.cards import endgame, operation
from engine.ops import A

from ._util import has_trait


def _friendly(loc):
    return has_trait(loc, "Starfleet", "Starbase")


@operation("1SIS01", 0, uses=[A.GAIN_RESOURCE],
           trigger=lambda ctx, ev: ev["kind"] == "take_control" and ev["seat"] == ctx.me.seat)
def emissary(ctx, actions):
    """REACTION: After you take control of a Location, gain 2 [Dilithium]."""
    yield from actions.gain_resource("dilithium", 2)


@operation("1SIS01", 1, uses=[A.SEND_AWAY_TEAM], requires=lambda ctx: any(_friendly(loc) for loc in ctx.all_locations()))
def posting(ctx, actions):
    """ACTIVATION: Send an [Away Team] to a Location with Starfleet/Starbase."""
    yield from actions.send_away_team(1, _friendly)


@endgame("1SIS01")
def sector(state, player):
    """ENDGAME: Score 1 [VP] for each controlled Location you have in play."""
    return len(player.locations)
