"""1SIS04 Orb of Prophecy and Change (Cargo, Development). Spec: resources/scans/base_game/cards/captains/sisko/1SIS04.md"""

from engine.cards import development_cost, operation
from engine.ops import A, DiscardFromHand, EffectCost, Spend

from ._util import has_trait, is_suit

development_cost("1SIS04", Spend(dilithium=3, latinum=2))


def _tired_bajorans(ctx):
    return [i for i in ctx.in_play() if i.exhausted and ctx.has(i, "Bajoran")]


def _refresh_a_bajoran(ctx, actions):
    card = yield from actions.pick_card("Refresh which Bajoran (cost)?", _tired_bajorans(ctx))
    yield from actions.refresh(card)


@operation("1SIS04", 0, uses=[A.REFRESH, A.DRAW],
           cost=[EffectCost(lambda ctx: bool(_tired_bajorans(ctx)), _refresh_a_bajoran, (A.REFRESH,),
                            "refresh a Bajoran")])
def vision(ctx, actions):
    """PLAY: Refresh a Bajoran to draw a card. Ruling: it must be exhausted."""
    yield from actions.draw(1)


@operation("1SIS04", 1, uses=[A.DISCARD, A.FIND], cost=[DiscardFromHand(1)])
def guidance(ctx, actions):
    """PLAY: Discard a card to find a Bajoran."""
    yield from actions.find(lambda i: has_trait(i, "Bajoran"), "a Bajoran")


@operation("1SIS04", 2, uses=[A.DISCARD, A.ENLIST_DEVELOPMENT, A.LOG],
           cost=[DiscardFromHand(1, lambda ctx, i: is_suit(i, "Person"), "a Person")])
def prophecy(ctx, actions):
    """PLAY: Discard a Person to enlist a Development, reducing the cost by 1 [Dilithium] and 1 [Latinum]. Log this
    card."""
    yield from actions.enlist_development(discount="both")
    yield from actions.log(ctx.this_card)
