"""2PER20 Su'Kal (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER20.md
Su'Kal cannot be played; the PASSIVE works once another effect promotes him. The SPECIAL before final scoring
arrives in Step 6."""

from engine.cards import operation
from engine.ops import A


@operation("2PER20", 0, uses=[A.GAIN_RESOURCE],
           trigger=lambda ctx, ev: ev["kind"] in ("take_incident", "return_incident") and ev["seat"] == ctx.me.seat)
def calm(ctx, actions):
    """PASSIVE: Whenever you take or return an Incident, gain 1 [Dilithium]."""
    yield from actions.gain_resource("dilithium", 1)
