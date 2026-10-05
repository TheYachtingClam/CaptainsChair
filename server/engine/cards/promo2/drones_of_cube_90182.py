"""0ALL01 Drones of Cube 90182 (Ally, promo). Spec: resources/scans/promo2/cards/ally/0ALL01.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import has_trait, ships


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


@operation("0ALL01", 1, uses=[A.DRAW, A.GAIN_SPECIALTY], cost=[Spend(dilithium=1)],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and has_trait(ctx.event_card, "Borg"))
def link_up(ctx, actions):
    """SUPPORT: After putting a Borg into play, spend 1 [Dilithium] to draw a card and gain 2 [Research]."""
    yield from actions.draw(1)
    yield from actions.gain_specialty("research", 2)


@operation("0ALL01", 2, uses=[A.DRAW], requires=lambda ctx: False,
           trigger=lambda ctx, ev: ev["kind"] == "assimilate")
def assimilated(ctx, actions):
    """SUPPORT: Requires [Borg] 5. After assimilating a card gain 1 [Borg] and draw 2 cards.
    Ruling: the Borg track and assimilation have no rules in these boxes (KW-DRONE-01), so it never triggers."""
    return
    yield  # pragma: no cover
