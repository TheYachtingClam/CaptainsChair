"""2KHA12 Vacated Regula I (Location). Spec: resources/scans/to_boldly_go/cards/captains/kahn/2KHA12.md"""

from engine.cards import operation
from engine.ops import A, EffectCost, TakeIncidentCost

from ._util import has_trait, ships


def _destroy_a_development(ctx, actions):
    card = yield from actions.pick_card("Destroy which card from your Development pile (cost)?", list(ctx.me.development))
    yield from actions.destroy(card)


@operation("2KHA12", 0, uses=[A.TAKE_CONTROL],
           requires=lambda ctx: any(s.at in {loc.uid for loc in ctx.state.neutral} for s in ships(ctx)))
def occupy(ctx, actions):
    """PLAY: If you have a Ship at a neutral Location, take control of this location."""
    yield from actions.take_control(ctx.this_card)


@operation("2KHA12", 1, uses=[A.TAKE_INCIDENT, A.MARK_TRAIT])
def records(ctx, actions):
    """CONTROL: You may take an Incident to mark one trait of a card in the Junk pile."""
    cards = [i for i in ctx.state.junk if ctx.can_mark(i)]
    if not cards or not ctx.state.incident:
        return
    if (yield from actions.may("Take an Incident to mark one trait of a card in the Junk?")):
        yield from actions.take_incident()
        chosen = yield from actions.pick_card("Mark a trait of which card in the Junk?", cards)
        yield from actions.mark_trait(chosen)


@operation("2KHA12", 2, uses=[A.RETURN_INCIDENT],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and has_trait(ctx.event_card, "Scientist")
           and bool(ctx.hand_incidents("discard")))
def research_staff(ctx, actions):
    """REACTION: After putting a Scientist into play, return an Incident from your hand or Discard pile."""
    incident = yield from actions.pick_card("Return which Incident?", ctx.hand_incidents("discard"))
    if incident is not None:
        yield from actions.return_incident(incident)


@operation("2KHA12", 3, uses=[A.TAKE_INCIDENT, A.DESTROY, A.GAIN_RESOURCE],
           cost=[TakeIncidentCost(), EffectCost(lambda ctx: bool(ctx.me.development), _destroy_a_development,
                                                (A.DESTROY,), "destroy a card from your Development pile")])
def strip_the_station(ctx, actions):
    """ACTIVATION: Take an Incident and destroy a card from your Development pile to gain 1 [Glory]."""
    yield from actions.gain_resource("glory", 1)
