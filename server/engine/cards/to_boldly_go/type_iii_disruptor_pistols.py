"""2CAR17 Type III Disruptor Pistols (Cargo). Spec: resources/scans/to_boldly_go/cards/cargo/2CAR17.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, others_in_hand


def _armed(i) -> bool:
    return has_trait(i, "Klingon", "Romulan", "Breen")


@operation("2CAR17", 0, uses=[A.GAIN_SPECIALTY, A.JUNK, A.DISCARD, A.ATTACK, A.REMOVE_AWAY_TEAM, A.GAIN_RESOURCE])
def ambush(ctx, actions):
    """ATTACK PLAY: Gain 1 [Military]. Junk a card from the Market. You may discard a Klingon/Romulan/Breen to remove
    up to 2 opponent [Away Team] from the same Location. Gain 1 [Glory] for each [Away Team] removed.
    Cadet: the virtual opponent has 1 Away Team at each neutral Location, so 1 is removed (REQ-CTM-12)."""
    yield from actions.gain_specialty("military", 1)
    yield from actions.junk()
    opp = ctx.opponent
    targets = [loc for loc in ctx.all_locations() if ctx.away_at(loc, opp) > 0] if opp is not None \
        else list(ctx.state.neutral)
    if not targets or not others_in_hand(ctx, _armed):
        return
    if not (yield from actions.may("Discard a Klingon, Romulan or Breen to remove opponent Away Teams?")):
        return
    yield from actions.discard(1, pred=_armed, label="a Klingon, Romulan or Breen")
    if not (yield from actions.attack(removes_away_teams=True)):
        return
    loc = yield from actions.pick_card("Remove opponent Away Teams from which Location?", targets)
    if opp is None:
        yield from actions.gain_resource("glory", 1)
        return
    removed = 0
    for _ in range(min(2, ctx.away_at(loc, opp))):
        if removed and not (yield from actions.may("Remove a second Away Team there?")):
            break
        yield from actions.remove_away_team(loc, opp)
        removed += 1
    yield from actions.gain_resource("glory", removed)
