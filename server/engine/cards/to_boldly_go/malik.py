"""2PER12 Malik (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER12.md"""

from engine.cards import operation, skill_icons
from engine.ops import A, DiscardFromHand, LogFromHand, traits_of

from ._util import has_trait


@operation("2PER12", 1, uses=[A.LOG, A.ENLIST_DEVELOPMENT],
           cost=[LogFromHand(lambda ctx, i: has_trait(i, "Human", "Klingon"), "a Human or Klingon", ("hand", "discard"))])
def augment_program(ctx, actions):
    """PLAY: Log a Human/Klingon from your hand or Discard pile to enlist a Development and log this card."""
    yield from actions.enlist_development()
    yield from actions.log(ctx.this_card)


@operation("2PER12", 3, uses=[A.DISCARD, A.GAIN_ACTION], cost=[DiscardFromHand(1)],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and has_trait(ctx.event_card, "Attack"))
def aggression(ctx, actions):
    """REACTION: After putting an Attack into play (including this), discard a card to gain an [Action]."""
    yield from actions.gain_action(1)


@operation("2PER12", 0, uses=[A.DISCARD, A.ATTACK, A.STEAL],
           cost=[DiscardFromHand(1, lambda ctx, i: has_trait(i, "Weapon"), "a Weapon")])
def augment_strike(ctx, actions):
    """ATTACK PLAY: Discard a Weapon to steal 1 [Glory]."""
    if (yield from actions.attack()):
        yield from actions.steal("glory", 1)


@skill_icons("2PER12")
def augment_skills(state, owner, inst):
    """PASSIVE: This card has 1 [Military] for each Augment you have in play (including this, max 3).
    Each of the 3 Variable icons is Military while that many Augments are in play; the rest have no icon."""
    from engine.ops import Ctx
    from engine.state import OpRef

    ctx = Ctx(state, OpRef(mode="auto", seat=owner.seat))
    augments = ctx.count_in_play(lambda i: "Augment" in traits_of(state, i))
    return ["Military"] * min(3, augments)
