"""3FRE10 Shax (Person, Development). Spec: resources/scans/second_contact/cards/captains/freeman/3FRE10.md"""

from engine.cards import development_cost, operation
from engine.ops import A, LogFromHand, Spend

from ._util import is_suit

development_cost("3FRE10", Spend(dilithium=2))


@operation("3FRE10", 0, uses=[A.LOG, A.GAIN_RESOURCE, A.RETURN_INCIDENT],
           cost=[LogFromHand(lambda ctx, i: is_suit(i, "Ship"), "a Ship")])
def tactical(ctx, actions):
    """PLAY: Log a Ship from your hand. Gain 2 [Glory]. You may return up to 2 Incident."""
    yield from actions.gain_resource("glory", 2)
    for n in (1, 2):
        incident = yield from actions.pick_card(f"Return an Incident ({n} of up to 2)?", ctx.hand_incidents(),
                                                optional=True, none_label="Stop")
        if not incident:
            break
        yield from actions.return_incident(incident)


def _neutral_with_opponent(ctx):
    if ctx.opponent is None:
        return list(ctx.state.neutral) if ctx.virtual_opponent else []  # one virtual Away Team at each (REQ-CTM-12)
    return [loc for loc in ctx.state.neutral if ctx.away_at(loc, ctx.opponent)]


@operation("3FRE10", 1, uses=[A.ATTACK, A.REMOVE_AWAY_TEAM, A.GAIN_RESOURCE])
def suppress(ctx, actions):
    """ATTACK ACTIVATION: Remove an opponent [Away Team] from a neutral Location. Gain 1 [Glory]."""
    targets = _neutral_with_opponent(ctx)
    if targets and (yield from actions.attack(removes_away_teams=True)):
        loc = yield from actions.pick_card("Remove an opponent Away Team from which Location?", targets)
        if ctx.opponent is not None:
            yield from actions.remove_away_team(loc, ctx.opponent)
        yield from actions.gain_resource("glory", 1)


@operation("3FRE10", 2, uses=[A.DRAW_FROM_LOG],
           trigger=lambda ctx, ev: ev["kind"] == "log" and ev.get("uid") == ctx.ref.uid)
def back_again(ctx, actions):
    """SPECIAL: After you log this card, draw it from your Log."""
    if ctx.this_card in ctx.me.log:
        yield from actions.draw_from_log(lambda i: i.uid == ctx.this_card.uid, "Shax")
