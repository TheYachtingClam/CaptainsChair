"""2KHA09 Infiltrate (Directive, Development). Spec: resources/scans/to_boldly_go/cards/captains/kahn/2KHA09.md"""

from engine.cards import development_cost, operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import has_trait, ships

development_cost("2KHA09", Spend(latinum=2))


@operation("2KHA09", 0, uses=[A.WARP])
def slip_past(ctx, actions):
    """PLAY: You may warp up to 3 of your Ship with Cloak."""
    warped: set[str] = set()
    for n in (1, 2, 3):
        cloaked = [s for s in ships(ctx) if has_trait(s, "Cloak") and s.uid not in warped]
        ship = yield from actions.pick_card(f"Warp a Ship with Cloak ({n} of up to 3)?", cloaked, optional=True,
                                            none_label="Stop")
        if ship is None:
            break
        warped.add(ship.uid)
        yield from actions.warp(ship)


@operation("2KHA09", 1, uses=[A.GAIN_CARD], cost=[DiscardFromHand(2), Spend(dilithium=1)])
def recruit(ctx, actions):
    """PLAY: Discard 2 cards and spend 1 [Dilithium] to gain a Person/Cargo/Ally."""
    yield from actions.gain_card(["Person", "Cargo", "Ally"], label="a Person, Cargo or Ally")
