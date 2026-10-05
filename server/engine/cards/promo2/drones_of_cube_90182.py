"""0ALL01 Drones of Cube 90182 (Ally, promo). Spec: resources/scans/promo2/cards/ally/0ALL01.md
The SUPPORT operations arrive in Step 7."""

from engine.cards import operation
from engine.ops import A

from ._util import ships


@operation("0ALL01", 0, uses=[A.BEAM, A.REFRESH, A.DRAW, A.SPEND], requires=lambda ctx: bool(ships(ctx)))
def link(ctx, actions):
    """PLAY: Beam this card to a Ship. Either: refresh that Ship OR draw a card OR spend 1 [Dilithium] to do both."""
    ship = yield from actions.pick_card("Beam the Drones to which Ship?", ships(ctx))
    yield from actions.beam(ctx.this_card, ship)
    options = [("refresh", "Refresh that Ship"), ("draw", "Draw a card")]
    if actions.can_spend(dilithium=1):
        options.append(("both", "Spend 1 Dilithium to do both"))
    choice = yield from actions.choose("Drones of Cube 90182: choose one.", options)
    if choice == "both":
        yield from actions.spend(dilithium=1)
    if choice in ("refresh", "both"):
        yield from actions.refresh(ship)
    if choice in ("draw", "both"):
        yield from actions.draw(1)
