"""1ALL06 Emerald Chain (Ally). Spec: resources/scans/base_game/cards/ally/1ALL06.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait


@operation("1ALL06", 0, uses=[A.GAIN_SPECIALTY, A.ATTACK, A.STEAL, A.FREE_PLAY])
def extort(ctx, actions):
    """ATTACK PLAY: Gain 1 [Military]. Steal 1 [Dilithium]. You may free play a Business."""
    yield from actions.gain_specialty("military", 1)
    if (yield from actions.attack()):
        yield from actions.steal("dilithium", 1)
    this = ctx.this_card
    cards = [i for i in actions.free_play_candidates(lambda i: has_trait(i, "Business")) if i.uid != this.uid]
    card = yield from actions.pick_card("Free play a Business?", cards, optional=True, none_label="No")
    if card:
        yield from actions.free_play(card)
