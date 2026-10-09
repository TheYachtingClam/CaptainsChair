"""1KOL19 Klingon Disruptors (Cargo). Spec: resources/scans/base_game/cards/captains/koloth/1KOL19.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, others_in_hand


def _klingon(i):
    return has_trait(i, "Klingon")


@operation("1KOL19", 0, uses=[A.DISCARD, A.ATTACK, A.REMOVE_AWAY_TEAM, A.GAIN_RESOURCE])
def open_fire(ctx, actions):
    """ATTACK PLAY: Discard a Klingon. If you do, up to twice: remove an opponent [Away Team] from a neutral Location
    where you have an [Away Team]. Gain 1 [Glory] for each [Away Team] removed.
    Cadet: the virtual opponent has 1 Away Team at each neutral Location (REQ-CTM-12)."""
    if not others_in_hand(ctx, _klingon):
        return
    yield from actions.discard(1, pred=_klingon, label="a Klingon")
    if not (yield from actions.attack(removes_away_teams=True)):
        return
    opp = ctx.opponent
    hit: set[str] = set()
    for n in (1, 2):
        targets = [loc for loc in ctx.state.neutral if ctx.away_at(loc) > 0
                   and (ctx.away_at(loc, opp) > 0 if opp is not None else loc.uid not in hit)]
        loc = yield from actions.pick_card(f"Remove an opponent Away Team from which Location ({n} of up to 2)?",
                                           targets, optional=True, none_label="Stop")
        if not loc:
            break
        hit.add(loc.uid)
        if opp is not None:
            yield from actions.remove_away_team(loc, opp)
        yield from actions.gain_resource("glory", 1)


@operation("1KOL19", 1, uses=[A.GAIN_SPECIALTY])
def drill(ctx, actions):
    """PLAY: Gain 1 [Military]."""
    yield from actions.gain_specialty("military", 1)
