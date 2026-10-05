"""2LOC14 Khitomer (Location). Spec: resources/scans/to_boldly_go/cards/location/2LOC14.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait


@operation("2LOC14", 0, uses=[A.FREE_PLAY])
def accords(ctx, actions):
    """CONTROL: You may free play a Starfleet."""
    cards = actions.free_play_candidates(lambda i: has_trait(i, "Starfleet"))
    card = yield from actions.pick_card("Free play a Starfleet?", cards, optional=True, none_label="No")
    if card:
        yield from actions.free_play(card)


@operation("2LOC14", 1, uses=[A.TAKE_INCIDENT],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] != ctx.me.seat
           and ctx.event_card is not None and "Attack" in ctx.traits(ctx.event_card))
def treaty_violation(ctx, actions):
    """REACTION: After your opponent puts an Attack into play, they take an Incident. This is not an Attack."""
    yield from actions.take_incident(opponent=True)


@operation("2LOC14", 2, uses=[A.GAIN_ACTION],
           trigger=lambda ctx, ev: ev["kind"] == "log" and ev.get("by") == ctx.me.seat and ctx.event_card is not None
           and ("Attack" in ctx.traits(ctx.event_card) or ctx.has_specialty_icon(ctx.event_card, "military")))
def peace(ctx, actions):
    """REACTION: After you log an Attack or a card with [Military]/[Military Focus], gain an [Action]."""
    yield from actions.gain_action(1)
