"""2KIRK03 Starfleet Headquarters (Location). Spec: resources/scans/to_boldly_go/cards/captains/kirk/2KIRK03.md"""

from engine.cards import operation
from engine.ops import A

from ._util import stardate_sequence


@operation("2KIRK03", 0, uses=[A.SEND_AWAY_TEAM],
           trigger=lambda ctx, ev: ev["kind"] == "log" and ev.get("uid") == ctx.ref.uid and ev.get("by") == ctx.me.seat)
def recall_to_hq(ctx, actions):
    """SPECIAL: When you log this card, up to X times, where X is the sequence number of the current Stardate card:
    send an [Away Team] to a Location."""
    times = stardate_sequence(ctx.state)
    for n in range(1, times + 1):
        if not (yield from actions.may(f"Send an Away Team to a Location ({n} of up to {times})?")):
            break
        if (yield from actions.send_away_team(1)) is None:
            break
