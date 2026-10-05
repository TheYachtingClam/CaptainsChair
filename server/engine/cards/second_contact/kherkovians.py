"""3PIK06 Kherkovians (Ally, Development). Spec: resources/scans/second_contact/cards/captains/pike/3PIK06.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend, TakeIncidentCost

from ._util import count_traits, species_of

development_cost("3PIK06", Spend(dilithium=3), TakeIncidentCost())


@operation("3PIK06", 0, uses=[A.FIND])
def many_faces(ctx, actions):
    """PLAY: Find a card with multiple Different Species."""
    yield from actions.find(lambda i: len(species_of(i)) >= 2, "a card with multiple Different Species")


@operation("3PIK06", 1, uses=[A.SCAN, A.GAIN_RESOURCE, A.LOG], requires=lambda ctx: ctx.track("research") >= 9)
def cure(ctx, actions):
    """PLAY: Requires [Research] 9. Scan 2 of either Person, Cargo, or Ally. Gain 1 [Glory] for each Different Species
    on the gained card. Gain 1 [Glory] if you have another Doctor in play. Log this card."""
    suit = yield from actions.choose("Scan 2 of which suit?", [(s, s) for s in ("Person", "Cargo", "Ally")])
    gained = yield from actions.scan(2, [suit])
    glory = len(species_of(gained)) if gained else 0
    if count_traits(ctx, "Doctor", exclude=ctx.this_card):
        glory += 1
    if glory:
        yield from actions.gain_resource("glory", glory)
    yield from actions.log(ctx.this_card)
