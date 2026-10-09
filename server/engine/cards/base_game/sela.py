"""1SEL01 Sela (Captain). Spec: resources/scans/base_game/cards/captains/sela/1SEL01.md"""

from engine.cards import endgame, operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import has_trait, owned_cards

SCHEMES = ("Infiltrate", "Conquer")


@operation("1SEL01", 0, uses=[A.GAIN_RESOURCE],
           trigger=lambda ctx, ev: ev["kind"] == "attacked" and ev.get("attacker") == ctx.me.seat)
def spoils(ctx, actions):
    """REACTION: After attacking your opponent, gain 1 [Dilithium]/[Latinum]."""
    kind = yield from actions.choose("Gain which?", [("dilithium", "1 Dilithium"), ("latinum", "1 Latinum")])
    yield from actions.gain_resource(kind, 1)


@operation("1SEL01", 1, uses=[A.DISCARD, A.SCAN_FOR],
           cost=[DiscardFromHand(1, lambda ctx, i: ctx.name(i) in SCHEMES, "Infiltrate or Conquer"), Spend(latinum=3)])
def recruit_agents(ctx, actions):
    """ACTIVATION: Discard either Infiltrate or Conquer and spend 3 [Latinum] to scan for either Klingon, Vulcan, or
    Starfleet."""
    trait = yield from actions.choose("Scan for which?", [(t, t) for t in ("Klingon", "Vulcan", "Starfleet")])
    yield from actions.scan_for(lambda i: has_trait(i, trait), f"a {trait}")


@endgame("1SEL01")
def schemes(state, player):
    """ENDGAME: Score 1 [VP] for each of your Attack cards, excluding cards with Romulan/Reman."""
    return sum(1 for i in owned_cards(player) if has_trait(i, "Attack") and not has_trait(i, "Romulan", "Reman"))
