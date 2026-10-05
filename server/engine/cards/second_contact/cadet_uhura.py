"""3PIK24 Cadet Uhura (Person). Spec: resources/scans/second_contact/cards/captains/pike/3PIK24.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import has_trait


@operation("3PIK24", 0, uses=[A.GAIN_CARD], cost=[Spend(dilithium=2)])
def hail(ctx, actions):
    """PLAY: Spend 2 [Dilithium] to gain a Person/Ally."""
    yield from actions.gain_card(["Person", "Ally"], label="a Person or Ally")


@operation("3PIK24", 1, uses=[A.GAIN_CARD], cost=[Spend(dilithium=2)], requires=lambda ctx: ctx.track("influence") >= 5)
def linguist(ctx, actions):
    """PLAY: Requires [Influence] 5. Spend 2 [Dilithium] to gain an Alien, including from the Junk."""
    yield from actions.gain_card(None, lambda i: has_trait(i, "Alien"), "an Alien", from_junk=True)


@operation("3PIK24", 2, uses=[A.DISCARD, A.DRAW_FROM_DISCARD], cost=[DiscardFromHand(1)],
           trigger=lambda ctx, ev: ev["kind"] == "exhaust" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and ctx.event_card.card == "3PIK02")
def translation(ctx, actions):
    """REACTION: After exhausting Improbable, Unstoppable, Sensational, discard a card to draw a card from your Discard
    pile."""
    yield from actions.draw_from_discard()
