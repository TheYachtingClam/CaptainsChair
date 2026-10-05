"""2ALL02 Bolians (Ally). Spec: resources/scans/to_boldly_go/cards/ally/2ALL02.md"""

from engine.cards import operation
from engine.ops import A


@operation("2ALL02", 0, uses=[A.GAIN_SPECIALTY, A.DRAW, A.FREE_PLAY])
def draw_and_play(ctx, actions):
    """PLAY: Gain 1 [Influence]. Draw a card. You may free play the drawn card."""
    yield from actions.gain_specialty("influence", 1)
    before = list(ctx.me.hand)
    yield from actions.draw(1)
    drawn = [i for i in ctx.me.hand if i not in before]
    playable = actions.free_play_candidates(lambda i: i in drawn)
    if playable and (yield from actions.may(f"Free play {ctx.name(playable[0])}?")):
        yield from actions.free_play(playable[0])
