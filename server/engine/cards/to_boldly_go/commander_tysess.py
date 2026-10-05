"""2PER04 Commander Tysess (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER04.md
The PLAY duplicates, which arrives in Step 6."""

from engine.cards import operation
from engine.ops import A, Spend


@operation("2PER04", 1, uses=[A.TRIGGER_CONTROL], cost=[Spend(dilithium=1)],
           trigger=lambda ctx, ev: ev["kind"] == "send_away_team" and ev["seat"] == ctx.me.seat and ev.get("controlled"))
def andorian_command(ctx, actions):
    """REACTION: After sending an [Away Team] to a controlled Location, spend 1 [Dilithium] to trigger that card's
    control operation."""
    loc = next((l for l in ctx.me.locations if l.uid == ctx.event.get("location")), None)
    if loc is not None:
        yield from actions.trigger_control(loc)
