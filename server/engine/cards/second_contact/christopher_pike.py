"""3PIK01 Christopher Pike (Captain). Spec: resources/scans/second_contact/cards/captains/pike/3PIK01.md"""

from engine import cards as registry
from engine.cards import operation
from engine.ops import A, LogFromHand

from ._util import has_trait, is_suit

# PASSIVE: Operations that find, free play, or return Incident from your hand can also target cards from your Log.
registry.INCIDENTS_FROM_LOG.add("3PIK01")


@operation("3PIK01", 0, uses=[A.LOG, A.GAIN_RESOURCE],
           cost=[LogFromHand(lambda ctx, i: is_suit(i, "Incident"), "an Incident")],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and has_trait(ctx.event_card, "Time Travel"))
def temporal_burden(ctx, actions):
    """REACTION: After putting a Time Travel into play, log an Incident (from your hand) to gain 1 [Glory]."""
    yield from actions.gain_resource("glory", 1)
