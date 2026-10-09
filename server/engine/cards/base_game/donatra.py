"""1SEL04 Donatra (Person, Development). Spec: resources/scans/base_game/cards/captains/sela/1SEL04.md"""

from engine.cards import development_cost, operation
from engine.ops import A, DiscardFromHand, DismissFromPlay, Spend

from ._util import is_suit, ships

development_cost("1SEL04", Spend(dilithium=2))


@operation("1SEL04", 0, uses=[A.DRAW, A.SPEND, A.DISCARD, A.REFRESH])
def commander(ctx, actions):
    """PLAY: Draw 3 cards. For each: spend 1 [Dilithium] OR discard it. Refresh a Ship."""
    before = [i.uid for i in ctx.me.hand]
    yield from actions.draw(3)
    for card in [i for i in ctx.me.hand if i.uid not in before]:
        keep = actions.can_spend(dilithium=1) and (
            yield from actions.may(f"Spend 1 Dilithium to keep {ctx.name(card)}? Otherwise it is discarded."))
        if keep:
            yield from actions.spend(dilithium=1)
        else:
            yield from actions.discard(1, pred=lambda i: i.uid == card.uid)
    ship = yield from actions.pick_card("Refresh which Ship?", [s for s in ships(ctx) if s.exhausted])
    if ship:
        yield from actions.refresh(ship)


@operation("1SEL04", 1, uses=[A.DISCARD, A.WARP], cost=[DiscardFromHand(1)],
           requires=lambda ctx: bool(ships(ctx)))
def flank(ctx, actions):
    """ACTIVATION: Discard a card to warp a Ship."""
    ship = yield from actions.pick_card("Warp which Ship?", [s for s in ships(ctx) if actions.can_warp(s)])
    if ship:
        yield from actions.warp(ship)


@operation("1SEL04", 2, uses=[A.DISMISS, A.DRAW], cost=[DismissFromPlay(lambda ctx, i: is_suit(i, "Ship"), "a Ship")])
def scuttle(ctx, actions):
    """ACTIVATION: Dismiss a Ship to draw 2 cards."""
    yield from actions.draw(2)
