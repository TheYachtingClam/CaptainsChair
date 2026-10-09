"""1SEL14 Tomalak (Person). Spec: resources/scans/base_game/cards/captains/sela/1SEL14.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import has_trait, is_suit


@operation("1SEL14", 0, uses=[A.GAIN_CARD, A.ATTACK, A.DISMISS, A.FORCE, A.DISCARD], cost=[Spend(dilithium=2)])
def ultimatum(ctx, actions):
    """ATTACK PLAY: Spend 2 [Dilithium] to gain a Ship. Dismiss all of your opponent's Starfleet Duty Officers. If any
    were dismissed, force them to discard a card."""
    yield from actions.gain_card(["Ship"], label="a Ship")
    opp = ctx.opponent
    if not (yield from actions.attack()) or opp is None:
        return
    officers = [i for i in opp.duty if "Starfleet" in ctx.traits(i)]
    for officer in officers:
        yield from actions.dismiss(officer)
    if officers:
        yield from actions.discard(1, player=opp)


@operation("1SEL14", 1, uses=[A.DRAW_FROM_DISCARD], cost=[Spend(dilithium=1)],
           requires=lambda ctx: any(is_suit(i, "Ship") for i in ctx.me.discard))
def refit(ctx, actions):
    """ACTIVATION: Spend 1 [Dilithium] to draw a Ship from your Discard pile."""
    yield from actions.draw_from_discard(lambda i: is_suit(i, "Ship"), "a Ship")


@operation("1SEL14", 2, uses=[A.DISCARD, A.DRAW_FROM_DISCARD], cost=[DiscardFromHand(1)],
           requires=lambda ctx: any(has_trait(i, "Attack") for i in ctx.me.discard))
def regroup(ctx, actions):
    """ACTIVATION: Discard a card to draw an Attack from your Discard pile."""
    paid = actions.paid[0].uid if actions.paid else None
    yield from actions.draw_from_discard(lambda i: has_trait(i, "Attack") and i.uid != paid, "an Attack")
