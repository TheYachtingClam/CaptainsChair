"""3FRE07 T88 Diagnostic Tool (Cargo, Ongoing, Development). Spec: resources/scans/second_contact/cards/captains/freeman/3FRE07.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import ships

development_cost("3FRE07", Spend(dilithium=2))


@operation("3FRE07", 0, uses=[A.REFRESH, A.DEPLOY])
def calibrate(ctx, actions):
    """PLAY: You may refresh a Ship. Deploy this card."""
    ship = yield from actions.pick_card("Refresh a Ship?", [s for s in ships(ctx) if s.exhausted], optional=True,
                                        none_label="No")
    if ship:
        yield from actions.refresh(ship)
    yield from actions.deploy(ctx.this_card)


@operation("3FRE07", 1, uses=[A.SCAN],
           trigger=lambda ctx, ev: ev["kind"] == "would_gain_market" and ev["seat"] == ctx.me.seat
           and bool(ev.get("suits")))
def diagnostic(ctx, actions):
    """REACTION: When you would gain a card, scan 2 of the same suit instead. With a gain that offers a choice of
    suits ("a Person or a Cargo") you choose which of them to scan. Not offered for a gain by trait."""
    yield from actions.scan(2, list(ctx.event["suits"]))
    return True
