"""1CAR04 Ferengi Wine (Cargo). Spec: resources/scans/base_game/cards/cargo/1CAR04.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import count_traits


@operation("1CAR04", 0, uses=[A.GAIN_RESOURCE], requires=lambda ctx: ctx.track("influence") >= 5)
def vintage(ctx, actions):
    """PLAY: Requires [Influence] 5. Gain 1 [Latinum] for each Ferengi and each Business you have in play (max 5). If
    you gained at least 3 [Latinum] this way, gain 1 [Glory]. Ruling: a card with both traits counts twice."""
    n = min(5, count_traits(ctx, "Ferengi") + count_traits(ctx, "Business"))
    if n:
        yield from actions.gain_resource("latinum", n)
    if n >= 3:
        yield from actions.gain_resource("glory", 1)


@operation("1CAR04", 1, uses=[A.SCAN, A.JUNK], cost=[Spend(latinum=2)])
def tasting(ctx, actions):
    """PLAY: Spend 2 [Latinum] to scan 1 of Ally, including from the Junk. Junk a card from the Market."""
    yield from actions.scan(1, ["Ally"], include_junk=True)
    yield from actions.junk()
