"""3FRE12 T'Ana (Person). Spec: resources/scans/second_contact/cards/captains/freeman/3FRE12.md"""

from engine.cards import operation, skill_icons
from engine.ops import A

from ._util import is_suit


@operation("3FRE12", 0, uses=[A.GAIN_SPECIALTY, A.RETURN_INCIDENT])
def chief_medical(ctx, actions):
    """PLAY: Gain 1 [Research]. You may return an Incident from your Discard pile."""
    yield from actions.gain_specialty("research", 1)
    incidents = [i for i in ctx.me.discard if is_suit(i, "Incident")]
    incident = yield from actions.pick_card("Return an Incident from your Discard pile?", incidents, optional=True,
                                            none_label="No")
    if incident:
        yield from actions.return_incident(incident)


@operation("3FRE12", 1, uses=[A.RETURN_INCIDENT, A.PUT, A.GAIN_ACTION],
           trigger=lambda ctx, ev: ev["kind"] == "take_incident" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and ctx.event_card in ctx.me.hand)
def no_nonsense(ctx, actions):
    """REACTION: After taking an Incident, return it, then put this card on the bottom of your deck and gain an
    [Action]."""
    yield from actions.return_incident(ctx.event_card)
    yield from actions.put_on_deck(ctx.this_card, bottom=True)
    yield from actions.gain_action(1)


@skill_icons("3FRE12")
def research(state, owner, inst):
    """PASSIVE: This card has 1 [Research]."""
    return ["Research"]
