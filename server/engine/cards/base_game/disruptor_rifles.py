"""1SEL15 Disruptor Rifles (Cargo). Spec: resources/scans/base_game/cards/captains/sela/1SEL15.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, others_in_hand


def _romulan(i):
    return has_trait(i, "Romulan")


@operation("1SEL15", 0, uses=[A.DISCARD, A.ATTACK, A.REMOVE_AWAY_TEAM, A.GAIN_RESOURCE, A.JUNK])
def open_fire(ctx, actions):
    """ATTACK PLAY: Discard a Romulan. If you do, up to twice: remove an opponent [Away Team] from a neutral Location
    where you have a Ship. Gain 1 [Glory] for each [Away Team] removed. You may junk a card from the Market.
    Cadet: the virtual opponent has 1 Away Team at each neutral Location (REQ-CTM-12)."""
    if others_in_hand(ctx, _romulan):
        yield from actions.discard(1, pred=_romulan, label="a Romulan")
        if (yield from actions.attack(removes_away_teams=True)):
            opp = ctx.opponent
            hit: set[str] = set()
            for n in (1, 2):
                targets = [loc for loc in ctx.state.neutral if ctx.ships_at(loc)
                           and (ctx.away_at(loc, opp) > 0 if opp is not None else loc.uid not in hit)]
                loc = yield from actions.pick_card(f"Remove an opponent Away Team from which Location ({n} of up to "
                                                   "2)?", targets, optional=True, none_label="Stop")
                if not loc:
                    break
                hit.add(loc.uid)
                if opp is not None:
                    yield from actions.remove_away_team(loc, opp)
                yield from actions.gain_resource("glory", 1)
    if (yield from actions.may("Junk a card from the Market?")):
        yield from actions.junk()


@operation("1SEL15", 1, uses=[A.GAIN_SPECIALTY, A.JUNK])
def drill(ctx, actions):
    """PLAY: Gain 1 [Military]. Junk a card from the Market."""
    yield from actions.gain_specialty("military", 1)
    yield from actions.junk()
