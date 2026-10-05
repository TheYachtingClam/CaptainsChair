"""3PIK23 Joseph M'Benga (Person). Spec: resources/scans/second_contact/cards/captains/pike/3PIK23.md"""

from engine.cards import operation
from engine.ops import A


@operation("3PIK23", 0, uses=[A.GAIN_SPECIALTY, A.RETURN_INCIDENT, A.JUNK, A.GAIN_RESOURCE])
def doctor(ctx, actions):
    """PLAY: Gain 1 [Research]. You may return an Incident. Junk a Person from the Market, if able. If you do both,
    gain 1 [Glory]."""
    yield from actions.gain_specialty("research", 1)
    incident = yield from actions.pick_card("Return an Incident?", ctx.hand_incidents(), optional=True, none_label="No")
    if incident:
        yield from actions.return_incident(incident)
    junked = yield from actions.junk(["Person"])
    if incident and junked:
        yield from actions.gain_resource("glory", 1)


@operation("3PIK23", 1, uses=[A.SEND_AWAY_TEAM], requires=lambda ctx: ctx.track("military") >= 5)
def field_medic(ctx, actions):
    """RESUPPLY: Requires [Military] 5. You may send an [Away Team] to a Location where you have a Ship."""
    if any(ctx.ships_at(loc) for loc in ctx.all_locations()) and (
            yield from actions.may("Send an Away Team to a Location where you have a Ship?")):
        yield from actions.send_away_team(1, where=lambda loc: bool(ctx.ships_at(loc)))


def _military_discard(ctx, ev):
    if ev["kind"] != "discard" or ev["seat"] != ctx.me.seat or ev.get("step") != "action" or ctx.event_card is None:
        return False
    icons = ctx.skills(ctx.event_card)
    return ("Military" in icons or "Any" in icons) and bool(ctx.hand_incidents("discard"))


@operation("3PIK23", 2, uses=[A.RETURN_INCIDENT], trigger=_military_discard)
def treatment(ctx, actions):
    """REACTION: After discarding a card with [Military]/[Any Skill] during your Action step, return an Incident from
    your hand or Discard pile."""
    incident = yield from actions.pick_card("Return which Incident?", ctx.hand_incidents("discard"))
    if incident:
        yield from actions.return_incident(incident)
