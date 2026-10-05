"""2SOV06 T'Pau (Person, Development). Spec: resources/scans/to_boldly_go/cards/captains/soval/2SOV06.md"""

from engine.cards import development_cost, operation, skill_icons
from engine.ops import A, Spend

from ._util import is_suit

development_cost("2SOV06", Spend(glory=2))


@operation("2SOV06", 0, uses=[A.DRAW, A.RETURN_INCIDENT, A.GAIN_RESOURCE, A.PROMOTE])
def reconciliation(ctx, actions):
    """PLAY: Draw a card. Both players may return an Incident from their hand or Discard pile. For each Incident
    returned, gain 1 [Glory]. You may promote a Person from your hand or Staging Area to Duty Officer (can be this
    card). Ruling: each player returns at most one; the opponent's choice is not an attack."""
    yield from actions.draw(1)
    returned = 0
    for player in [ctx.me] + ([ctx.opponent] if ctx.opponent else []):
        incidents = [i for i in player.hand + player.discard if is_suit(i, "Incident")]
        incident = yield from actions.pick_card("T'Pau: return an Incident from your hand or Discard pile?", incidents,
                                                optional=True, none_label="No", seat=player.seat)
        if incident:
            yield from actions.return_incident(incident)
            returned += 1
    if returned:
        yield from actions.gain_resource("glory", returned)
    people = [i for i in ctx.me.hand + ctx.me.staging if is_suit(i, "Person")]
    person = yield from actions.pick_card("Promote a Person from your hand or Staging Area?", people, optional=True,
                                          none_label="No")
    if person:
        yield from actions.promote(person)


@skill_icons("2SOV06")
def any_skills(state, owner, inst):
    """PASSIVE: This card has 2 [Any Skill] (only while on duty)."""
    return ["Any", "Any"]
