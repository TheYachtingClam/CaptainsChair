"""1BUR13 Hugh Culber (Person). Spec: resources/scans/base_game/cards/captains/burnham/1BUR13.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import is_suit


@operation("1BUR13", 0, uses=[A.FIND, A.FREE_PLAY, A.GAIN_RESOURCE])
def sickbay(ctx, actions):
    """PLAY: You may find a Person/Incident. You may free play an Incident to gain 1 [Glory]."""
    yield from actions.find(lambda i: is_suit(i, "Person", "Incident"), "a Person or an Incident", optional=True)
    incident = yield from actions.pick_card("Free play an Incident to gain 1 Glory?",
                                            actions.free_play_candidates(lambda i: is_suit(i, "Incident")),
                                            optional=True, none_label="No")
    if incident:
        yield from actions.free_play(incident)
        yield from actions.gain_resource("glory", 1)


@operation("1BUR13", 1, uses=[A.DISCARD, A.RETURN_INCIDENT, A.GAIN_SPECIALTY],
           cost=[DiscardFromHand(1, lambda ctx, i: is_suit(i, "Person", "Directive"), "a Person or a Directive")],
           trigger=lambda ctx, ev: ev["kind"] == "take_incident" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and any(i.uid == ctx.event_card.uid for i in ctx.me.hand))
def treatment(ctx, actions):
    """REACTION: After taking an Incident, discard a Person/Directive to return it and gain 1 [Research]."""
    incident = next((i for i in ctx.me.hand if i.uid == ctx.event_card.uid), None)
    if incident is not None:
        yield from actions.return_incident(incident)
    yield from actions.gain_specialty("research", 1)
