"""1SIS22 Jadzia Dax (Person). Spec: resources/scans/base_game/cards/captains/sisko/1SIS22.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import incidents_in_hand

TRACKS = ("research", "influence", "military")


def _gain_lowest(ctx, actions):
    low = min(ctx.track(t) for t in TRACKS)
    tied = [t for t in TRACKS if ctx.track(t) == low]
    track = tied[0] if len(tied) == 1 else (
        yield from actions.choose("Gain 1 on which of your lowest tracks?", [(t, t.capitalize()) for t in tied]))
    yield from actions.gain_specialty(track, 1)


@operation("1SIS22", 0, uses=[A.GAIN_SPECIALTY, A.SPEND])
def lifetimes(ctx, actions):
    """PLAY: Gain 1 [Research]/[Influence]/[Military], whichever is the lowest (you choose in a tie). You may spend 1
    [Latinum] to do this a second time."""
    yield from _gain_lowest(ctx, actions)
    if actions.can_spend(latinum=1) and (yield from actions.may("Spend 1 Latinum to do this a second time?")):
        yield from actions.spend(latinum=1)
        yield from _gain_lowest(ctx, actions)


@operation("1SIS22", 1, uses=[A.RETURN_INCIDENT, A.GAIN_RESOURCE], cost=[Spend(latinum=1)],
           requires=lambda ctx: bool(incidents_in_hand(ctx)))
def science_station(ctx, actions):
    """PLAY: Spend 1 [Latinum] to return an Incident and gain 1 [Glory]."""
    incident = yield from actions.pick_card("Return which Incident?", incidents_in_hand(ctx))
    yield from actions.return_incident(incident)
    yield from actions.gain_resource("glory", 1)


@operation("1SIS22", 2, uses=[A.SCAN],
           trigger=lambda ctx, ev: ev["kind"] == "would_gain_market" and ev["seat"] == ctx.me.seat
           and len(ev.get("suits") or []) == 1)
def curiosity(ctx, actions):
    """REACTION: When you would gain a card, scan 2 of the same suit instead. Only when the gain is of one suit, so
    "the same suit" is known (REQ-CORE-42)."""
    yield from actions.scan(2, list(ctx.event["suits"]))
    return True
