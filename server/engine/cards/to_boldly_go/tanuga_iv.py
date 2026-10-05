"""2LOC17 Tanuga IV (Location). Spec: resources/scans/to_boldly_go/cards/location/2LOC17.md"""

from engine.cards import operation
from engine.ops import A

from ._util import count_traits, has_trait


@operation("2LOC17", 0, uses=[A.SPEND, A.SCAN_FOR])
def research_station(ctx, actions):
    """CONTROL: You may spend 3 [Dilithium] to scan for either a Scientist or a Weapon."""
    if actions.can_spend(dilithium=3) and (yield from actions.may("Spend 3 Dilithium to scan for a Scientist or Weapon?")):
        yield from actions.spend(dilithium=3)
        trait = yield from actions.choose("Scan for which?", [("Scientist", "Scientist"), ("Weapon", "Weapon")])
        yield from actions.scan_for(lambda i: has_trait(i, trait), f"a {trait}")


@operation("2LOC17", 1, uses=[A.GAIN_RESOURCE])
def output(ctx, actions):
    """CLEAN-UP: Gain 1 [Latinum] for each Weapon you have in play (max 3) OR gain 1 [Dilithium] for each Scientist you
    have in play (max 4)."""
    weapons, scientists = min(3, count_traits(ctx, "Weapon")), min(4, count_traits(ctx, "Scientist"))
    choice = yield from actions.choose("Tanuga IV: choose one.",
                                       [("latinum", f"{weapons} Latinum (Weapons)"),
                                        ("dilithium", f"{scientists} Dilithium (Scientists)")])
    n = weapons if choice == "latinum" else scientists
    if n:
        yield from actions.gain_resource(choice, n)
