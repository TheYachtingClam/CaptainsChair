"""1BUR11 Trance Worm (Cargo, Development). Spec: resources/scans/base_game/cards/captains/burnham/1BUR11.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

development_cost("1BUR11", Spend(latinum=3))


@operation("1BUR11", 0, uses=[A.JUNK, A.SPEND, A.GAIN_CARD, A.LOG, A.GAIN_RESOURCE])
def trade(ctx, actions):
    """PLAY: Junk a card from the Market. Spend 1 [Latinum] to gain a Person or a Cargo and log it. If the gained
    card has 3 or more traits, gain 1 [Glory]."""
    yield from actions.junk()
    if not (yield from actions.spend(latinum=1)):
        return
    gained = yield from actions.gain_card(["Person", "Cargo"], label="a Person or a Cargo")
    if gained is None:
        return
    yield from actions.log(gained)
    if len(ctx.card(gained).traits) >= 3:
        yield from actions.gain_resource("glory", 1)
