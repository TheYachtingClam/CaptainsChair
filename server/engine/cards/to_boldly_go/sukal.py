"""2PER20 Su'Kal (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER20.md
Su'Kal cannot be played; the PASSIVE works once another effect promotes him."""

from engine import cards as registry
from engine.cards import operation
from engine.ops import A, owned_everywhere

from ._util import is_suit


@operation("2PER20", 0, uses=[A.GAIN_RESOURCE],
           trigger=lambda ctx, ev: ev["kind"] in ("take_incident", "return_incident") and ev["seat"] == ctx.me.seat)
def calm(ctx, actions):
    """PASSIVE: Whenever you take or return an Incident, gain 1 [Dilithium]."""
    yield from actions.gain_resource("dilithium", 1)


@operation("2PER20", 1, uses=[A.FIND, A.RETURN_INCIDENT])
def peace_of_mind(ctx, actions):
    """SPECIAL: Before scoring, find and return up to 2 Incident. Runs at the start of final scoring wherever you own
    Su'Kal; returned Incidents no longer score their negative VP."""
    for n in (1, 2):
        incidents = [i for i in owned_everywhere(ctx.me) if is_suit(i, "Incident")]
        incident = yield from actions.pick_card(f"Su'Kal: return an Incident before scoring ({n} of up to 2)?",
                                                incidents, optional=True, none_label="Stop")
        if not incident:
            break
        yield from actions.return_incident(incident)


registry.BEFORE_SCORING.add("2PER20")
