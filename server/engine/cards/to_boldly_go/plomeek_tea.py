"""2SOV13 Plomeek Tea (Cargo). Spec: resources/scans/to_boldly_go/cards/captains/soval/2SOV13.md"""

from engine.cards import operation
from engine.ops import MARKET_SUITS, A


@operation("2SOV13", 0, uses=[A.REFRESH, A.SPEND, A.SWAP_JUNK_WITH_MARKET])
def tea_ceremony(ctx, actions):
    """PLAY: You may refresh your Captain and a Duty Officer. You may spend 1 [Latinum] to swap a card in the Junk with
    the card of the same suit in the Market."""
    if ctx.me.captain.exhausted and (yield from actions.may("Refresh your Captain?")):
        yield from actions.refresh(ctx.me.captain)
    tired = [i for i in ctx.me.duty if i.exhausted]
    officer = yield from actions.pick_card("Refresh a Duty Officer?", tired, optional=True, none_label="No")
    if officer:
        yield from actions.refresh(officer)
    swappable = [i for i in ctx.state.junk if ctx.suit(i) in MARKET_SUITS
                 and not (ctx.state.market.get(ctx.suit(i)) is not None and ctx.state.market[ctx.suit(i)].res)]
    if swappable and actions.can_spend(latinum=1):
        card = yield from actions.pick_card("Spend 1 Latinum to swap a Junk card into the Market?", swappable,
                                            optional=True, none_label="No")
        if card:
            yield from actions.spend(latinum=1)
            yield from actions.swap_junk_with_market(card)


@operation("2SOV13", 1, uses=[A.GAIN_RESOURCE])
def brew(ctx, actions):
    """PLAY: Gain 1 [Latinum]."""
    yield from actions.gain_resource("latinum", 1)
