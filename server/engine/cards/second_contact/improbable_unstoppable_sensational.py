"""3PIK02 Improbable, Unstoppable, Sensational (Status). Spec: resources/scans/second_contact/cards/captains/pike/3PIK02.md"""

from engine.cards import operation
from engine.ops import A

from ._util import count_traits

TRACKS = ("research", "influence", "military")


@operation("3PIK02", 0, uses=[A.GAIN_SPECIALTY, A.SPEND])
def reputation(ctx, actions):
    """CLEAN-UP: If you have no Shady/Attack in play, gain 1 [Influence]; otherwise spend 1 [Glory], if able."""
    if not count_traits(ctx, "Shady", "Attack"):
        yield from actions.gain_specialty("influence", 1)
    elif actions.can_spend(glory=1):
        yield from actions.spend(glory=1)


def _skilled_arrival(ctx, ev):
    return (ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat and not ev.get("beamed")
            and ctx.event_card is not None and bool(ctx.skills(ctx.event_card)))


@operation("3PIK02", 1, uses=[A.GAIN_SPECIALTY], trigger=_skilled_arrival)
def sensational(ctx, actions):
    """REACTION: After you put a card with one or more Skill icons into play (excluding beaming), gain 1 on the
    Specialty track matching one of those icons. Any Skill matches any track."""
    icons = ctx.skills(ctx.event_card)
    tracks = [t for t in TRACKS if t.capitalize() in icons or "Any" in icons]
    track = tracks[0] if len(tracks) == 1 else (
        yield from actions.choose("Gain 1 on which track?", [(t, t.capitalize()) for t in tracks]))
    yield from actions.gain_specialty(track, 1)
