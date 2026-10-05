"""3PER02 Barry Waddle (Person, Reward). Spec: resources/scans/second_contact/cards/rewards/3PER02.md"""

from engine import cards as registry
from engine.cards import hand_size_modifier, operation
from engine.ops import A

from ._util import minus_unless_logged

registry.VP_SPECIAL["3PER02"] = minus_unless_logged(2)  # SPECIAL: If not logged, this card scores -2.


@operation("3PER02", 0, uses=[A.ATTACK, A.STEAL, A.SPEND, A.SCAN_FOR])
def rough_trade(ctx, actions):
    """ATTACK PLAY: Steal 2 [Dilithium]. You may spend 2 [Latinum] to scan for [Influence Focus]."""
    if (yield from actions.attack()):
        yield from actions.steal("dilithium", 2)
    if actions.can_spend(latinum=2) and (yield from actions.may("Spend 2 Latinum to scan for an Influence Focus card?")):
        yield from actions.spend(latinum=2)
        yield from actions.scan_for(lambda i: ctx.card(i).focus == "Influence", "a card with an Influence Focus")


@hand_size_modifier("3PER02")
def larger_hand(state, owner, size):
    """PASSIVE: Increase your hand size by 1."""
    return size + 1


def _sharing(ctx):
    mine = ctx.traits(ctx.this_card)
    return [i for i in ctx.in_play(beamed=False) if i is not ctx.this_card and i.exhausted and ctx.traits(i) & mine]


@operation("3PER02", 2, uses=[A.REFRESH], requires=lambda ctx: ctx.track("influence") >= 5,
           trigger=lambda ctx, ev: ev["kind"] == "spend" and ev["seat"] == ctx.me.seat and ev.get("latinum")
           and ctx.track("influence") >= 5 and bool(_sharing(ctx)))
def business_partner(ctx, actions):
    """REACTION: Requires [Influence] 5. After spending [Latinum], refresh another card that shares a trait with this
    card."""
    card = yield from actions.pick_card("Refresh which card?", _sharing(ctx))
    if card:
        yield from actions.refresh(card)
