"""1BUR21 Joann Owosekun (Person). Spec: resources/scans/base_game/cards/captains/burnham/1BUR21.md"""

from engine.cards import operation
from engine.ops import A, EffectCost

from ._util import ships

DISCOVERY = "1BUR03"


def _discovery(ctx):
    return next((s for s in ctx.me.fleet if s.card == DISCOVERY), None)


@operation("1BUR21", 0, uses=[A.SEND_AWAY_TEAM, A.BEAM, A.GAIN_RESOURCE])
def ops_station(ctx, actions):
    """PLAY: You may send an [Away Team] to the U.S.S. Discovery-A's Location. You may beam a card from your hand or
    Discard pile to the U.S.S. Discovery-A. If you do both, gain 1 [Glory]."""
    ship = _discovery(ctx)
    if ship is None:
        return
    done = 0
    loc = ctx.location_of(ship)
    if loc is not None and any(t.uid == loc.uid for t in actions.away_targets()) and ctx.me.away_pool > 0 and (
            yield from actions.may(f"Send an Away Team to {ctx.name(loc)}?")):
        yield from actions.send_away_team(1, target=loc)
        done += 1
    pool = [i for i in [*ctx.me.hand, *ctx.me.discard] if i.uid != ctx.this_card.uid]
    card = yield from actions.pick_card("Beam a card from your hand or Discard pile to the U.S.S. Discovery-A?", pool,
                                        optional=True, none_label="No")
    if card:
        yield from actions.beam(card, _discovery(ctx))
        done += 1
    if done == 2:
        yield from actions.gain_resource("glory", 1)


@operation("1BUR21", 1, uses=[A.DISCARD, A.GAIN_RESOURCE])
def long_watch(ctx, actions):
    """RESUPPLY: Discard the top card of your deck and gain 1 [Latinum]."""
    yield from actions.discard_from_deck()
    yield from actions.gain_resource("latinum", 1)


def _ready_ships(ctx):
    return [s for s in ships(ctx) if not s.exhausted and ctx.location_of(s) is not None]


def _exhaust_a_ship(ctx, actions):
    ship = yield from actions.pick_card("Exhaust which Ship (cost)?", _ready_ships(ctx))
    yield from actions.exhaust(ship)
    actions.paid.append(ship)


@operation("1BUR21", 2, uses=[A.EXHAUST, A.REFRESH],
           cost=[EffectCost(lambda ctx: bool(_ready_ships(ctx)), _exhaust_a_ship, (A.EXHAUST,), "exhaust a Ship")])
def relay(ctx, actions):
    """ACTIVATION: Exhaust a Ship to refresh its Location."""
    loc = ctx.location_of(actions.paid[0]) if actions.paid else None
    if loc is not None:
        yield from actions.refresh(loc)
