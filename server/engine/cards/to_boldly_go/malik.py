"""2PER12 Malik (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER12.md
The attack PLAY arrives in Step 4 and the Skill-icon PASSIVE in Step 5."""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, LogFromHand

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
