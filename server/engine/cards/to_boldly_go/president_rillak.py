"""2PER15 President Rillak (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER15.md"""

from engine.cards import duty_slots, operation
from engine.ops import A

from ._util import is_suit


def _beamed_incidents(ctx):
    return [b for host in ctx.in_play(beamed=False) for b in host.beamed if is_suit(b, "Incident")]


@operation("2PER15", 0, uses=[A.RETURN_INCIDENT, A.GAIN_RESOURCE])
def diplomacy(ctx, actions):
    """PLAY: Return any number of beamed Incident. If you returned at least 2 Incident this way, gain 2 [Glory]."""
    returned = 0
    while _beamed_incidents(ctx):
        card = yield from actions.pick_card("Return a beamed Incident?", _beamed_incidents(ctx), optional=True,
                                            none_label="Stop")
        if not card:
            break
        yield from actions.return_incident(card)
        returned += 1
    if returned >= 2:
        yield from actions.gain_resource("glory", 2)


@operation("2PER15", 1, uses=[A.GAIN_ACTION],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev.get("played") and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and ctx.name(ctx.event_card) in ("Utilize", "Inspire"))
def inspired(ctx, actions):
    """REACTION: After playing Utilize or Inspire, gain an [Action]."""
    yield from actions.gain_action(1)


@duty_slots("2PER15")
def ambassador_officer(state, owner, inst):
    """PASSIVE: You may additionally have another Person with Ambassador on duty."""
    return ["Ambassador"]
