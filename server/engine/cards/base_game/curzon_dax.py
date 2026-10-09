"""1KOL06 Curzon Dax (Person, Development). Spec: resources/scans/base_game/cards/captains/koloth/1KOL06.md"""

from engine.cards import development_cost, operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import incidents_in_hand

development_cost("1KOL06", Spend(dilithium=2, latinum=2))


@operation("1KOL06", 0, uses=[A.GAIN_SPECIALTY])
def mediator(ctx, actions):
    """PLAY: Gain 1 [Influence]/[Military], whichever is the lower (you choose in a tie)."""
    influence, military = ctx.track("influence"), ctx.track("military")
    if influence == military:
        track = yield from actions.choose("Gain 1 on which track?", [("influence", "Influence"), ("military", "Military")])
    else:
        track = "influence" if influence < military else "military"
    yield from actions.gain_specialty(track, 1)


@operation("1KOL06", 1, uses=[A.RETURN_INCIDENT], requires=lambda ctx: bool(incidents_in_hand(ctx)))
def smooth_over(ctx, actions):
    """PLAY: Return an Incident."""
    incident = yield from actions.pick_card("Return which Incident?", incidents_in_hand(ctx))
    yield from actions.return_incident(incident)


@operation("1KOL06", 2, uses=[A.DISCARD, A.SCAN], cost=[DiscardFromHand(1)])
def old_friends(ctx, actions):
    """ACTIVATION: Discard a card to scan 2 of Ally."""
    yield from actions.scan(2, ["Ally"])
