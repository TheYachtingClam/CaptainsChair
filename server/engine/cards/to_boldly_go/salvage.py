"""2REB17 Salvage (Directive), and Khan's identical copy 2KHA15.
Specs: resources/scans/to_boldly_go/cards/captains/rebner/2REB17.md and captains/kahn/2KHA15.md"""

from engine.cards import operation
from engine.ops import A, EffectCost, Spend

IDS = ("2REB17", "2KHA15")


def _junk_one(ctx, actions):
    yield from actions.junk()


@operation(IDS, 0, uses=[A.JUNK, A.DRAW], cost=[EffectCost(
    lambda ctx: any(i is not None and not i.res for i in ctx.state.market.values()), _junk_one, (A.JUNK,),
    "junk a card from the Market")])
def scrap(ctx, actions):
    """PLAY: Junk a card from the Market to draw a card."""
    yield from actions.draw(1)


@operation(IDS, 1, uses=[A.GAIN_CARD], cost=[Spend(latinum=1)])
def reclaim(ctx, actions):
    """PLAY: Spend 1 [Latinum] to gain a Person / Cargo / Ship / Ally from the Junk to your Discard pile."""
    yield from actions.gain_card(["Person", "Cargo", "Ship", "Ally"], label="a card from the Junk", only_junk=True)
