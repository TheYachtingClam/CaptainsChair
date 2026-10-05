"""2ARC06 Commander Shran (Person, Development). Spec: resources/scans/to_boldly_go/cards/captains/archer/2ARC06.md"""

from engine.cards import development_cost, operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import has_trait, is_suit

development_cost("2ARC06", Spend(dilithium=2, latinum=2))


@operation("2ARC06", 0, uses=[A.SCAN_FOR, A.DRAW])
def imperial_guard(ctx, actions):
    """PLAY: Scan for either an Andorian or a Weapon. Draw a card."""
    trait = yield from actions.choose("Scan for which?", [("Andorian", "Andorian"), ("Weapon", "Weapon")])
    yield from actions.scan_for(lambda i: has_trait(i, trait), f"a {trait}")
    yield from actions.draw(1)


@operation("2ARC06", 1, uses=[A.DISCARD, A.SEND_AWAY_TEAM, A.GAIN_RESOURCE], cost=[DiscardFromHand(1)])
def raid(ctx, actions):
    """ACTIVATION: Discard a card to send an [Away Team] to a Location. If the discarded card is a Directive/Cargo,
    gain 2 [Dilithium]."""
    yield from actions.send_away_team(1)
    if is_suit(actions.paid[0], "Directive", "Cargo"):
        yield from actions.gain_resource("dilithium", 2)


@operation("2ARC06", 2, uses=[A.ADD_AWAY_TEAM],
           trigger=lambda ctx, ev: ev["kind"] == "enlist" and ev.get("uid") == ctx.ref.uid and ev["seat"] == ctx.me.seat)
def andorian_guard(ctx, actions):
    """SPECIAL: When enlisting this card, add 2 [Away Team] from the supply (Archer's set-aside teams) to your
    Captain."""
    yield from actions.add_away_team(2)
