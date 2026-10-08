"""1PER04 Ambassador Kamarag (Person). Spec: resources/scans/base_game/cards/person/1PER04.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import has_trait


@operation("1PER04", 0, uses=[A.GAIN_SPECIALTY, A.SCAN_FOR], cost=[Spend(dilithium=2)])
def demand(ctx, actions):
    """PLAY: Spend 2 [Dilithium] to gain 1 [Military] and you may scan for either a Klingon or a Starfleet."""
    yield from actions.gain_specialty("military", 1)
    choice = yield from actions.choose("Scan for a Klingon or a Starfleet?",
                                       [("Klingon", "A Klingon"), ("Starfleet", "A Starfleet"), ("none", "No")])
    if choice != "none":
        yield from actions.scan_for(lambda i: has_trait(i, choice), f"a {choice}")


@operation("1PER04", 1, uses=[A.RETURN_INCIDENT],
           trigger=lambda ctx, ev: ev["kind"] == "take_control" and ev["seat"] != ctx.me.seat
           and bool(ctx.hand_incidents("discard")))
def protest(ctx, actions):
    """REACTION: After your opponent takes control of a Location, return an Incident from your hand or Discard pile."""
    incident = yield from actions.pick_card("Return which Incident?", ctx.hand_incidents("discard"))
    if incident:
        yield from actions.return_incident(incident)
