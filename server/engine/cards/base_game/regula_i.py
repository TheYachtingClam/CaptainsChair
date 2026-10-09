"""1LOC15 Regula I (Location). Spec: resources/scans/base_game/cards/location/1LOC15.md
Not the same card as Khan's Vacated Regula I (2KHA12)."""

from engine.cards import endgame, operation
from engine.ops import A

from ._util import has_trait, owned_cards


def _scientist(i):
    return has_trait(i, "Scientist")


@operation("1LOC15", 0, uses=[A.FIND, A.SPEND, A.SCAN_FOR])
def laboratory(ctx, actions):
    """CONTROL: You may find a Scientist OR you may spend 3 [Dilithium] to scan for Scientist."""
    options = [("find", "Find a Scientist")] + \
        ([("scan", "Spend 3 Dilithium to scan for a Scientist")] if actions.can_spend(dilithium=3) else []) + \
        [("none", "Neither")]
    choice = yield from actions.choose("Regula I: find a Scientist, or scan for one?", options)
    if choice == "find":
        yield from actions.find(_scientist, "a Scientist")
    elif choice == "scan":
        yield from actions.spend(dilithium=3)
        yield from actions.scan_for(_scientist, "a Scientist")


@operation("1LOC15", 1, uses=[A.GAIN_RESOURCE],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and ctx.has(ctx.event_card, "Scientist"))
def publication(ctx, actions):
    """REACTION: After putting a Scientist into play, gain 1 [Glory]."""
    yield from actions.gain_resource("glory", 1)


@endgame("1LOC15")
def anomalies(state, player):
    """ENDGAME: Score 1 [VP] for each of your Anomaly cards."""
    return sum(1 for i in owned_cards(player) if has_trait(i, "Anomaly"))
