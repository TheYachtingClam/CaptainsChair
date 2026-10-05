"""2ARC04 Founding the Federation (Directive, Development).
Spec: resources/scans/to_boldly_go/cards/captains/archer/2ARC04.md"""

from engine.cards import development_cost, operation
from engine.ops import SPECIES, A, Condition, Spend

from ._util import distinct_traits, earth_of, is_suit

development_cost("2ARC04", Spend(dilithium=1, latinum=1),
                 Condition(lambda ctx: distinct_traits(ctx.me.log, SPECIES) >= 5, "5+ Different Species logged"))


@operation("2ARC04", 0, uses=[A.ENLIST_RESERVE, A.GAIN_RESOURCE, A.BEAM, A.FIND, A.RETURN_INCIDENT, A.LOG])
def federation(ctx, actions):
    """PLAY: Enlist your entire Reserve deck. Gain all resources from Earth. You may beam up to 3 Ally from your Log to
    Earth. For each card beamed this way you may find and return an Incident. Log this card."""
    yield from actions.enlist_reserve(all_cards=True)
    earth = earth_of(ctx.me)
    if earth is not None:
        for kind, n in sorted(earth.res.items()):
            if n:
                yield from actions.gain_resource(kind, n, source=earth)
        for n in (1, 2, 3):
            allies = [i for i in ctx.me.log if is_suit(i, "Ally")]
            ally = yield from actions.pick_card(f"Beam an Ally from your Log to Earth ({n} of up to 3)?", allies,
                                                optional=True, none_label="Stop")
            if not ally:
                break
            yield from actions.beam(ally, earth)
            if (yield from actions.may("Find an Incident and return it?")):
                incident, _ = yield from actions.find(lambda i: is_suit(i, "Incident"), "an Incident", optional=True)
                if incident:
                    yield from actions.return_incident(incident)
    yield from actions.log(ctx.this_card)
