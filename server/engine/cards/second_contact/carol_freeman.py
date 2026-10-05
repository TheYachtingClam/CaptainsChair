"""3FRE01 Carol Freeman (Captain). Spec: resources/scans/second_contact/cards/captains/freeman/3FRE01.md"""

from engine.cards import endgame, operation
from engine.ops import A, DiscardFromHand

from ._util import is_suit


def cerritos(ctx):
    """Your deployed U.S.S. Cerritos, if any."""
    return next((s for s in ctx.me.fleet if s.card == "3FRE02"), None)


def _track_gained(ctx, ev):
    ship = cerritos(ctx)
    return (ev["kind"] == "gain_specialty" and ev["seat"] == ctx.me.seat and ev.get("amount", 1) > 0
            and ship is not None and ctx.location_of(ship) is not None)


@operation("3FRE01", 0, uses=[A.DISCARD, A.SEND_AWAY_TEAM],
           cost=[DiscardFromHand(1, lambda ctx, i: is_suit(i, "Person"), "a Person")], trigger=_track_gained)
def rally(ctx, actions):
    """REACTION: After gaining [Research]/[Influence]/[Military], discard a Person to send an [Away Team] to the
    location of the U.S.S. Cerritos."""
    yield from actions.send_away_team(1, target=ctx.location_of(cerritos(ctx)))


@operation("3FRE01", 1, uses=[A.WARP],
           trigger=lambda ctx, ev: ev["kind"] == "return_incident" and ev["seat"] == ctx.me.seat
           and cerritos(ctx) is not None)
def onwards(ctx, actions):
    """REACTION: After returning an Incident, warp the U.S.S. Cerritos."""
    yield from actions.warp(cerritos(ctx))


@endgame("3FRE01")
def captains_log(state, player):
    """ENDGAME: Score 1 [VP] for every 2 cards in your Log."""
    return len(player.log) // 2
