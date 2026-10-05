"""2SOV02 Vulcan Science Directorate (Status). Spec: resources/scans/to_boldly_go/cards/captains/soval/2SOV02.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait


@operation("2SOV02", 0, uses=[A.GAIN_RESOURCE],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and has_trait(ctx.event_card, "Anomaly", "Scientist"))
def research_grant(ctx, actions):
    """REACTION: After putting an Anomaly or a Scientist into play, gain 2 [Dilithium] or 1 [Glory]."""
    choice = yield from actions.choose("Gain 2 Dilithium or 1 Glory?", [("dil", "2 Dilithium"), ("glory", "1 Glory")])
    yield from actions.gain_resource("dilithium", 2) if choice == "dil" else actions.gain_resource("glory", 1)


@operation("2SOV02", 1, uses=[A.LOG],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and has_trait(ctx.event_card, "Time Travel"))
def temporal_prime_directive(ctx, actions):
    """PASSIVE: After putting a Time Travel into play, log this card. Mandatory, even while exhausted."""
    yield from actions.log(ctx.this_card)
