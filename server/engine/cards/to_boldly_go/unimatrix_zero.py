"""2ALL14 Unimatrix Zero (Ally). Spec: resources/scans/to_boldly_go/cards/ally/2ALL14.md"""

from engine.cards import operation
from engine.ops import A, can_afford

from ._util import count_traits


def _other_borg(ctx) -> int:
    return count_traits(ctx, "Borg", exclude=ctx.this_card)


@operation("2ALL14", 0, uses=[A.SPEND, A.DRAW, A.LOG],
           requires=lambda ctx: can_afford(ctx.me, dilithium=_other_borg(ctx)))
def collective(ctx, actions):
    """PLAY: Spend 1 [Dilithium] for each Borg you have in play (excluding this card). Draw 2 cards, and 1 more for
    each XB you have in play (max 6 cards total). If you have no other Borg in play, log this card."""
    borg = _other_borg(ctx)
    if borg:
        yield from actions.spend(dilithium=borg)
    yield from actions.draw(min(6, 2 + count_traits(ctx, "XB")))
    if not borg:
        yield from actions.log(ctx.this_card)
