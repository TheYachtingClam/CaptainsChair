"""1KOL14 Mara (Person). Spec: resources/scans/base_game/cards/captains/koloth/1KOL14.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import has_trait, is_suit, others_in_hand


def _outsider(i):
    return is_suit(i, "Person") and not has_trait(i, "Klingon")


@operation("1KOL14", 0, uses=[A.GAIN_SPECIALTY, A.DISCARD, A.GAIN_RESOURCE], cost=[Spend(dilithium=3)])
def science_officer(ctx, actions):
    """PLAY: Spend 3 [Dilithium] to gain 2 [Research]/[Influence]/[Military]. You may discard a Person without Klingon
    to gain 1 [Glory]."""
    track = yield from actions.choose("Gain 2 on which track?", [("research", "Research"), ("influence", "Influence"),
                                                                 ("military", "Military")])
    yield from actions.gain_specialty(track, 2)
    if others_in_hand(ctx, _outsider) and (yield from actions.may("Discard a non-Klingon Person to gain 1 Glory?")):
        yield from actions.discard(1, pred=_outsider, label="a Person without Klingon")
        yield from actions.gain_resource("glory", 1)


@operation("1KOL14", 1, uses=[A.GAIN_SPECIALTY])
def analysis(ctx, actions):
    """RESUPPLY: Gain 1 [Research]."""
    yield from actions.gain_specialty("research", 1)
