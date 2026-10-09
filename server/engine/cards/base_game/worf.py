"""1PIC23 Worf (Person). Spec: resources/scans/base_game/cards/captains/picard/1PIC23.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand


def _targets(ctx):
    opp = ctx.opponent
    if opp is None:
        return [loc for loc in ctx.state.neutral if ctx.away_at(loc) > 0] if ctx.virtual_opponent else []
    return [loc for loc in ctx.all_locations() if ctx.away_at(loc) > 0 and ctx.away_at(loc, opp) > 0]


@operation("1PIC23", 0, uses=[A.TAKE_INCIDENT, A.DISCARD, A.SEND_AWAY_TEAM])
def security_chief(ctx, actions):
    """PLAY: Take an Incident and discard it. Discard the top card of your deck. Send 2 [Away Team] to a neutral
    Location."""
    yield from actions.take_incident(to="discard")
    yield from actions.discard_from_deck()
    yield from actions.send_away_team(2, lambda loc: loc in ctx.state.neutral, same_location=True)


@operation("1PIC23", 1, uses=[A.DISCARD, A.ATTACK, A.REMOVE_AWAY_TEAM, A.GAIN_RESOURCE], cost=[DiscardFromHand(1)],
           requires=lambda ctx: bool(_targets(ctx)))
def honor(ctx, actions):
    """ATTACK ACTIVATION: Discard a card to remove an opponent [Away Team] from a Location where you have an [Away
    Team]. If you do, gain 1 [Glory]. Cadet: the virtual opponent has one at each neutral Location (REQ-CTM-12)."""
    if not (yield from actions.attack(removes_away_teams=True)):
        return
    loc = yield from actions.pick_card("Remove an opponent Away Team from which Location?", _targets(ctx))
    if loc is None:
        return
    if ctx.opponent is not None:
        yield from actions.remove_away_team(loc, ctx.opponent)
    yield from actions.gain_resource("glory", 1)
