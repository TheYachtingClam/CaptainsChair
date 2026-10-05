"""2SOV08 Kir'Shara (Cargo, Development). Spec: resources/scans/to_boldly_go/cards/captains/soval/2SOV08.md"""

from engine.cards import development_cost, operation
from engine.ops import A, DismissDutyOfficer, Spend

from ._util import has_trait

development_cost("2SOV08", Spend(dilithium=2, latinum=1), DismissDutyOfficer())


@operation("2SOV08", 0, uses=[A.TAKE_INCIDENT, A.TAKE_ENCOUNTER, A.LOG])
def path_of_surak(ctx, actions):
    """PLAY: If you have 7+ Vulcan in play (excluding your Captain), take an Incident to take the top Encounter card.
    Log this card."""
    vulcans = ctx.count_in_play(lambda i: i is not ctx.me.captain and has_trait(i, "Vulcan"))
    if vulcans >= 7:
        yield from actions.take_incident()
        yield from actions.take_encounter()
    yield from actions.log(ctx.this_card)
