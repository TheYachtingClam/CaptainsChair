"""1PIC13 Beverly Crusher (Person). Spec: resources/scans/base_game/cards/captains/picard/1PIC13.md"""

from engine.cards import operation
from engine.ops import A, EffectCost

from ._util import is_suit


@operation("1PIC13", 0, uses=[A.GAIN_SPECIALTY, A.RETURN_INCIDENT])
def sickbay(ctx, actions):
    """PLAY: Gain 1 [Research]. You may return an Incident from your Discard pile."""
    yield from actions.gain_specialty("research", 1)
    incidents = [i for i in ctx.me.discard if is_suit(i, "Incident")]
    incident = yield from actions.pick_card("Return an Incident from your Discard pile?", incidents, optional=True,
                                            none_label="No")
    if incident:
        yield from actions.return_incident(incident)


def _others(ctx):
    taken = ctx.event.get("uid")
    return [i for i in ctx.me.hand if i.uid != taken]


def _discard_another(ctx, actions):
    taken = ctx.event.get("uid")
    yield from actions.discard(1, pred=lambda i: i.uid != taken, label="a different card (cost)")


@operation("1PIC13", 1, uses=[A.DISCARD, A.RETURN_INCIDENT, A.GAIN_RESOURCE],
           cost=[EffectCost(lambda ctx: bool(_others(ctx)), _discard_another, (A.DISCARD,), "discard a different card")],
           trigger=lambda ctx, ev: ev["kind"] == "take_incident" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None)
def triage(ctx, actions):
    """REACTION: After taking an Incident, discard a different card to return the Incident and gain 1 [Glory]."""
    incident = ctx.event_card
    if incident is not None:
        yield from actions.return_incident(incident)
    yield from actions.gain_resource("glory", 1)
