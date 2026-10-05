"""2KIRK23 Leonard McCoy (Person). Spec: resources/scans/to_boldly_go/cards/captains/kirk/2KIRK23.md"""

from engine.cards import operation
from engine.ops import A

from ._util import is_suit


@operation("2KIRK23", 0, uses=[A.GAIN_SPECIALTY, A.RETURN_INCIDENT])
def doctor(ctx, actions):
    """PLAY: Gain 1 [Research]. You may return an Incident."""
    yield from actions.gain_specialty("research", 1)
    incidents = [i for i in ctx.me.hand if is_suit(i, "Incident")]
    card = yield from actions.pick_card("Return an Incident?", incidents, optional=True, none_label="No")
    if card:
        yield from actions.return_incident(card)


def _person_lost(ctx, ev) -> bool:
    if ctx.state.step != "action" or ctx.state.active != ctx.me.seat or ctx.event_card is None:
        return False
    if not is_suit(ctx.event_card, "Person"):
        return False
    return (ev["kind"] == "discard" and ev["seat"] == ctx.me.seat) or (ev["kind"] == "log" and ev.get("by") == ctx.me.seat)


@operation("2KIRK23", 1, uses=[A.FREE_PLAY], trigger=_person_lost)
def bedside_manner(ctx, actions):
    """REACTION: After discarding or logging a Person during your Action Step, free play an Incident from your hand or
    Discard pile."""
    incidents = actions.free_play_candidates(lambda i: is_suit(i, "Incident"), zones_=("hand", "discard"))
    card = yield from actions.pick_card("Free play which Incident?", incidents)
    if card:
        yield from actions.free_play(card)
