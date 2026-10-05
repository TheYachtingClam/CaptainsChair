"""2ARC11 Major Hayes, MACO (Person). Spec: resources/scans/to_boldly_go/cards/captains/archer/2ARC11.md"""

from engine.cards import operation
from engine.ops import A

from ._util import count_traits


@operation("2ARC11", 0, uses=[A.SEND_AWAY_TEAM])
def deploy_macos(ctx, actions):
    """PLAY: Send an [Away Team] to a Location."""
    yield from actions.send_away_team(1)


@operation("2ARC11", 1, uses=[A.LOG, A.GAIN_RESOURCE, A.JUNK])
def requisition(ctx, actions):
    """PLAY: You may log a card from your hand or Discard pile to gain all resources from a card in the Market. Junk a
    card from the Market. Ruling: taking the resources first lets that card be junked."""
    loaded = [i for i in ctx.state.market.values() if i is not None and i.res]
    cards = [i for i in ctx.me.hand + ctx.me.discard if i is not ctx.this_card]
    if loaded and cards:
        card = yield from actions.pick_card("Log a card to take all resources from a Market card?", cards, optional=True,
                                            none_label="No")
        if card:
            yield from actions.log(card)
            target = yield from actions.pick_card("Take the resources from which Market card?", loaded)
            for kind, n in sorted(target.res.items()):
                if n:
                    yield from actions.gain_resource(kind, n, source=target)
    yield from actions.junk()


@operation("2ARC11", 2, uses=[A.ATTACK, A.REMOVE_AWAY_TEAM, A.GAIN_RESOURCE, A.SEND_AWAY_TEAM, A.LOG],
           requires=lambda ctx: ctx.track("military") >= 3)
def clear_the_area(ctx, actions):
    """ATTACK ACTIVATION: Requires [Military] 3. Remove all opponent [Away Team] from a Location where you have a Ship.
    Gain 1 [Glory] for each [Away Team] removed. If you have a Security in play, you may send an [Away Team] to the same
    Location. Log this card. Cadet: the virtual opponent's 1 Away Team at a neutral Location gives 1 Glory."""
    opp = ctx.opponent
    places = [l for l in ctx.all_locations() if ctx.ships_at(l)]
    loc = yield from actions.pick_card("Clear which Location where you have a Ship?", places)
    if loc is not None and (yield from actions.attack(removes_away_teams=True)):
        if opp is None:
            if loc in ctx.state.neutral:
                yield from actions.gain_resource("glory", 1)
        else:
            removed = ctx.away_at(loc, opp)
            for _ in range(removed):
                yield from actions.remove_away_team(loc, opp)
            if removed:
                yield from actions.gain_resource("glory", removed)
    if loc is not None and count_traits(ctx, "Security") and (yield from actions.may("Send an Away Team there?")):
        yield from actions.send_away_team(1, target=loc)
    yield from actions.log(ctx.this_card)
