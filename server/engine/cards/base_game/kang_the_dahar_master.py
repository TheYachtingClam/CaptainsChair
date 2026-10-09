"""1KOL07 Kang, the Dahar Master (Person, Development). Spec: resources/scans/base_game/cards/captains/koloth/1KOL07.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Condition, Spend

development_cost("1KOL07", Spend(dilithium=4), Condition(lambda ctx: ctx.me.glory >= 8, "have 8+ Glory"))


def gained_influence(ctx, ev):
    return ev["kind"] == "gain_specialty" and ev["seat"] == ctx.me.seat and ev.get("track") == "influence" \
        and (ev.get("amount") or 0) >= 1


@operation("1KOL07", 0, uses=[A.RETURN_INCIDENT, A.GAIN_RESOURCE])
def vengeance(ctx, actions):
    """PLAY: Return an Incident from your hand or Discard pile and gain 1 [Glory]."""
    incident = yield from actions.pick_card("Return which Incident?", ctx.hand_incidents("discard"))
    if incident:
        yield from actions.return_incident(incident)
    yield from actions.gain_resource("glory", 1)


@operation("1KOL07", 1, uses=[A.DESTROY, A.TAKE_ENCOUNTER, A.GAIN_RESOURCE], requires=lambda ctx: ctx.me.glory >= 15)
def blood_oath(ctx, actions):
    """PLAY: If you have at least 15 [Glory], destroy this card to take the top Encounter and gain 3 [Glory]."""
    yield from actions.destroy(ctx.this_card)
    yield from actions.take_encounter()
    yield from actions.gain_resource("glory", 3)


@operation("1KOL07", 2, uses=[A.GAIN_SPECIALTY, A.GAIN_RESOURCE], trigger=gained_influence)
def renown(ctx, actions):
    """REACTION: After gaining at least 1 [Influence], gain 1 [Influence] and 1 [Glory]."""
    yield from actions.gain_specialty("influence", 1)
    yield from actions.gain_resource("glory", 1)
