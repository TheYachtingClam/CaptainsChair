"""3PER05 Ensign Boimler (Person, Reward). Spec: resources/scans/second_contact/cards/rewards/3PER05.md
Not the same card as Bradward Boimler in Freeman's deck."""

from engine import cards as registry
from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import is_suit, minus_unless_logged

registry.CANNOT_PROMOTE.add("3PER05")  # SPECIAL: This card cannot be promoted.
registry.VP_SPECIAL["3PER05"] = minus_unless_logged(2)  # SPECIAL: If not logged, this card scores -2.


@operation("3PER05", 0, uses=[A.DISCARD, A.GAIN_ACTION], cost=[DiscardFromHand(3)])
def overtime(ctx, actions):
    """PLAY: Discard 3 cards to gain an [Action]."""
    yield from actions.gain_action(1)


@operation("3PER05", 1, uses=[A.DUPLICATE],
           trigger=lambda ctx, ev: ev["seat"] == ctx.me.seat and ctx.event_card is not None
           and is_suit(ctx.event_card, "Person")
           and ((ev["kind"] == "junk" and ev.get("source") == "market") or ev["kind"] == "promote"))
def eager(ctx, actions):
    """SUPPORT: After you junk or promote a Person, duplicate a play operation of that card.
    Ruling: since Boimler cannot be promoted, a duplicated "promote this card" does nothing."""
    yield from actions.duplicate([ctx.event_card], label=ctx.name(ctx.event_card), optional=False)
