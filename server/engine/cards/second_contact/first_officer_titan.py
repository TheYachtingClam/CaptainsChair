"""3RIK16 First Officer (U.S.S. Titan) (Person). Spec: resources/scans/second_contact/cards/captains/william riker/3RIK16.md"""

from engine.cards import operation
from engine.ops import A

from ._util import count_traits, ships


@operation("3RIK16", 0, uses=[A.SPEND, A.GAIN_ACTION, A.GAIN_SPECIALTY, A.EXHAUST, A.RECALL])
def number_one(ctx, actions):
    """PLAY: If you have a Scientist in play, you may spend 2 [Dilithium] to gain an [Action]. If you have a Weapon in
    play, gain 1 [Military]. You may exhaust your Captain to recall a card beamed to a Ship."""
    if count_traits(ctx, "Scientist") and actions.can_spend(dilithium=2) and (
            yield from actions.may("Spend 2 Dilithium to gain an Action?")):
        yield from actions.spend(dilithium=2)
        yield from actions.gain_action(1)
    if count_traits(ctx, "Weapon"):
        yield from actions.gain_specialty("military", 1)
    beamed = [b for s in ships(ctx) for b in s.beamed]
    if beamed and not ctx.me.captain.exhausted:
        card = yield from actions.pick_card("Exhaust your Captain to recall a card beamed to a Ship?", beamed,
                                            optional=True, none_label="No")
        if card:
            yield from actions.exhaust(ctx.me.captain)
            yield from actions.recall(card)


@operation("3RIK16", 1, uses=[A.GAIN_CARD])
def requisition(ctx, actions):
    """ACTIVATION: Gain a Cargo."""
    yield from actions.gain_card(["Cargo"], label="a Cargo")
