"""1KOL22 Korax (Person). Spec: resources/scans/base_game/cards/captains/koloth/1KOL22.md"""

from engine.cards import operation
from engine.ops import A

from ._util import discard_their_top_card, has_trait, others_in_hand, ships

operation("1KOL22", 0, uses=[A.GAIN_RESOURCE, A.ATTACK, A.DISCARD, A.TAKE_INCIDENT])(discard_their_top_card)


@operation("1KOL22", 1, uses=[A.ADJUST_HAND_SIZE, A.GAIN_RESOURCE])
def idle_hands(ctx, actions):
    """CLEAN-UP: For each unspent [Action], temporarily increase your hand size by 1 and you may gain 1 [Glory]."""
    n = ctx.actions_left()
    if n <= 0:
        return
    yield from actions.adjust_hand_size(n)
    if (yield from actions.may(f"Gain {n} Glory for your unspent Action(s)?")):
        yield from actions.gain_resource("glory", n)


def _tired(ctx, pred):
    return [s for s in ships(ctx) if s.exhausted and pred(s)]


@operation("1KOL22", 2, uses=[A.REFRESH, A.DISCARD],
           requires=lambda ctx: bool(_tired(ctx, lambda s: s.card == "1KOL02" or has_trait(s, "Klingon"))))
def first_officer(ctx, actions):
    """ACTIVATION: Refresh the I.K.S. Gr'oth. You may discard a card to refresh another Ship with Klingon."""
    for groth in _tired(ctx, lambda s: s.card == "1KOL02"):
        yield from actions.refresh(groth)
    others = _tired(ctx, lambda s: s.card != "1KOL02" and has_trait(s, "Klingon"))
    if others and others_in_hand(ctx) and (yield from actions.may("Discard a card to refresh another Klingon Ship?")):
        yield from actions.discard(1)
        ship = yield from actions.pick_card("Refresh which Klingon Ship?", others)
        yield from actions.refresh(ship)
