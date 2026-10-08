"""1CAR09 Mek'leth (Cargo). Spec: resources/scans/base_game/cards/cargo/1CAR09.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import has_trait


@operation("1CAR09", 0, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.ATTACK, A.FORCE, A.REVEAL, A.GAIN_RESOURCE],
           cost=[DiscardFromHand(1)])
def duel(ctx, actions):
    """ATTACK PLAY: Discard a card to gain 1 [Military]. Force your opponent to reveal their hand. You may discard an
    Attack from their hand to gain 1 [Glory]. Against the Bot, which has no hand, you say whether it succeeded
    (REQ-SOLO-190)."""
    yield from actions.gain_specialty("military", 1)
    opp = ctx.opponent
    if opp is None or not (yield from actions.attack()):
        return
    if opp.bot is not None:
        if (yield from actions.bot_hand_attack(opp)):
            yield from actions.gain_resource("glory", 1)
        return
    hand = list(opp.hand)
    actions.emit(f"{opp.name} reveals their hand: {', '.join(ctx.name(c) for c in hand) or 'no cards'}.",
                 irreversible=True)
    attacks = [i for i in hand if has_trait(i, "Attack")]
    card = yield from actions.pick_card(f"Discard an Attack from {opp.name}'s hand to gain 1 Glory?", attacks,
                                        optional=True, none_label="No")
    if card:
        yield from actions.discard(1, pred=lambda i: i.uid == card.uid, player=opp)
        yield from actions.gain_resource("glory", 1)
