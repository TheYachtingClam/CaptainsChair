"""1SEL03 I.R.W. Valdore (Ship, Development). Spec: resources/scans/base_game/cards/captains/sela/1SEL03.md  Its PLAY is registered in irw_goraxus.py."""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import opponent_ships, others_in_hand

development_cost("1SEL03", Spend(dilithium=5))


@operation("1SEL03", 1, uses=[A.SPEND, A.WARP, A.BEAM])
def manoeuvre(ctx, actions):
    """ACTIVATION: You may spend 1 [Dilithium] to warp this ship and you may beam a card here."""
    if actions.can_spend(dilithium=1) and (yield from actions.may("Spend 1 Dilithium to warp this ship?")):
        yield from actions.spend(dilithium=1)
        yield from actions.warp(ctx.this_card)
    card = yield from actions.pick_card("Beam a card here?", others_in_hand(ctx), optional=True, none_label="No")
    if card:
        yield from actions.beam(card, ctx.this_card)


@operation("1SEL03", 2, uses=[A.DRAW, A.ATTACK, A.FORCE, A.DISMISS], cost=[Spend(dilithium=2)])
def broadside(ctx, actions):
    """ATTACK ACTIVATION: Spend 2 [Dilithium] to draw a card and force your opponent to dismiss a Ship."""
    yield from actions.draw(1)
    opp = ctx.opponent
    if (yield from actions.attack()) and opp is not None:
        ship = yield from actions.pick_card("I.R.W. Valdore: dismiss one of your Ships.", opponent_ships(ctx),
                                            seat=opp.seat)
        if ship:
            yield from actions.dismiss(ship)
