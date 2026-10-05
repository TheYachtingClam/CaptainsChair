"""2GEO22 Kamran Gant (Person). Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO22.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_suit, ships


@operation("2GEO22", 0, uses=[A.SEND_AWAY_TEAM, A.GAIN_RESOURCE])
def send_team(ctx, actions):
    """PLAY: Send an Away Team to a Location. If it is a controlled Location, gain 1 Dilithium."""
    loc = yield from actions.send_away_team(1)
    if loc is not None and loc in ctx.me.locations:
        yield from actions.gain_resource("dilithium", 1)


@operation("2GEO22", 1, uses=[A.GAIN_CARD, A.LOG])
def grab_spy(ctx, actions):
    """CLEAN-UP: If there is a Spy in the Market, gain it to your hand, and log this card."""
    if not any(i is not None and has_trait(i, "Spy") for i in ctx.state.market.values()):
        return
    yield from actions.gain_card(None, lambda i: has_trait(i, "Spy"), "a Spy", to_hand=True)
    yield from actions.log(ctx.this_card)


@operation("2GEO22", 2, uses=[A.REFRESH, A.ATTACK, A.REMOVE_AWAY_TEAM])
def security(ctx, actions):
    """ATTACK ACTIVATION: You may refresh a Ship. For each Directive you have in play: you may remove an
    opponent Away Team from a Location where you have a Ship."""
    exhausted = [s for s in ships(ctx) if s.exhausted]
    ship = yield from actions.pick_card("Refresh a Ship?", exhausted, optional=True, none_label="No")
    if ship:
        yield from actions.refresh(ship)
    opp = ctx.opponent
    if opp is None:
        return  # Cadet: the virtual opponent's Away Teams cannot be removed for any benefit
    directives = ctx.count_in_play(lambda i: is_suit(i, "Directive"))
    for _ in range(directives):
        targets = [loc for loc in ctx.all_locations() if ctx.ships_at(loc) and ctx.away_at(loc, opp) > 0]
        loc = yield from actions.pick_card("Remove an opponent Away Team from which Location?", targets,
                                           optional=True, none_label="Stop")
        if not loc:
            break
        if not (yield from actions.attack(removes_away_teams=True)):
            break
        yield from actions.remove_away_team(loc, opp)
