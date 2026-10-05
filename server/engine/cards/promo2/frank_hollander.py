"""0CAR02 Frank Hollander (Cargo, promo). Spec: resources/scans/promo2/cards/cargo/0CAR02.md"""

from engine.cards import operation
from engine.ops import A, LogFromHand

from ._util import has_trait, is_suit


@operation("0CAR02", 0, uses=[A.LOG, A.GAIN_RESOURCE, A.FREE_PLAY],
           cost=[LogFromHand(lambda ctx, i: is_suit(i, "Cargo"), "a Cargo", ("hand", "discard", "play"), include_self=True)])
def collect(ctx, actions):
    """PLAY: Log a Cargo from your hand, Discard pile, or in play to gain 1 [Glory]. You may free play a
    Hologram/Incident. Ruling: Frank Hollander may log himself."""
    yield from actions.gain_resource("glory", 1)
    cards = actions.free_play_candidates(lambda i: has_trait(i, "Hologram") or is_suit(i, "Incident"))
    card = yield from actions.pick_card("Free play a Hologram or Incident?", cards, optional=True, none_label="No")
    if card:
        yield from actions.free_play(card)
