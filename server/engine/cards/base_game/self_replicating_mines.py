"""1SIS06 Self-Replicating Mines (Cargo, Development). Spec: resources/scans/base_game/cards/captains/sisko/1SIS06.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import draw_two_discard_one

development_cost("1SIS06", Spend(dilithium=5))


@operation("1SIS06", 0, uses=[A.ATTACK, A.FORCE, A.DISCARD, A.DRAW, A.DEPLOY])
def lay_mines(ctx, actions):
    """ATTACK PLAY: Force your opponent to discard a card. Draw two cards and discard one of them. Deploy this card."""
    if (yield from actions.attack()) and ctx.opponent is not None:
        yield from actions.discard(1, player=ctx.opponent)
    yield from draw_two_discard_one(ctx, actions)
    yield from actions.deploy(ctx.this_card)


@operation("1SIS06", 1, uses=[A.GAIN_RESOURCE])
def blockade(ctx, actions):
    """RESUPPLY: Gain 1 [Glory]."""
    yield from actions.gain_resource("glory", 1)


@operation("1SIS06", 2, uses=[A.RECALL],
           trigger=lambda ctx, ev: ev["kind"] == "gain_specialty" and ev["seat"] != ctx.me.seat
           and ev.get("track") in ("influence", "military") and (ev.get("amount") or 0) > 0)
def sweep(ctx, actions):
    """REACTION: After your opponent gains [Influence]/[Military], recall this card."""
    yield from actions.recall(ctx.this_card)


@operation("1SIS06", 3, uses=[A.LOG],
           trigger=lambda ctx, ev: ev["kind"] == "would_attack" and ev["seat"] == ctx.me.seat)
def detonate(ctx, actions):
    """PASSIVE: When you would be attacked, ignore the negative effect and log this card. Mandatory."""
    actions.emit("Self-Replicating Mines: the attack's negative effect is ignored.")
    yield from actions.log(ctx.this_card)
    return True
