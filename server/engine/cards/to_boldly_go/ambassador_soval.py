"""2ARC07 Ambassador Soval (Person, Development). Not the Soval deck's Captain.
Spec: resources/scans/to_boldly_go/cards/captains/archer/2ARC07.md"""

from engine.cards import development_cost, operation
from engine.ops import A, DiscardFromHand, ExhaustCaptain, Spend

from ._util import has_trait

development_cost("2ARC07", Spend(dilithium=3), ExhaustCaptain())


@operation("2ARC07", 0, uses=[A.SCAN_FOR, A.DRAW])
def envoy(ctx, actions):
    """PLAY: Scan for either a Vulcan or a Scientist. Draw a card."""
    trait = yield from actions.choose("Scan for which?", [("Vulcan", "Vulcan"), ("Scientist", "Scientist")])
    yield from actions.scan_for(lambda i: has_trait(i, trait), f"a {trait}")
    yield from actions.draw(1)


@operation("2ARC07", 1, uses=[A.DISCARD, A.DRAW, A.GAIN_SPECIALTY],
           cost=[DiscardFromHand(1, lambda ctx, i: has_trait(i, "Human"), "a Human")])
def counsel(ctx, actions):
    """ACTIVATION: Discard a Human to draw 2 cards and gain 1 [Research]/[Influence]/[Military]."""
    yield from actions.draw(2)
    track = yield from actions.choose("Gain 1 on which track?", [(t, t.capitalize()) for t in
                                                                 ("research", "influence", "military")])
    yield from actions.gain_specialty(track, 1)


@operation("2ARC07", 2, uses=[A.ADD_AWAY_TEAM],
           trigger=lambda ctx, ev: ev["kind"] == "enlist" and ev.get("uid") == ctx.ref.uid and ev["seat"] == ctx.me.seat)
def vulcan_escort(ctx, actions):
    """SPECIAL: When enlisting this card, add 2 [Away Team] from the supply (Archer's set-aside teams) to your
    Captain."""
    yield from actions.add_away_team(2)
