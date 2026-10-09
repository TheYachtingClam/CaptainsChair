"""1SIS10 Worf, Son of Mogh (Person, Development). Spec: resources/scans/base_game/cards/captains/sisko/1SIS10.md  Not the same card as Worf (1PIC23)."""

from engine.cards import development_cost, operation
from engine.ops import A, DiscardFromHand, Spend

development_cost("1SIS10", Spend(dilithium=2))


def _targets(ctx):
    opp = ctx.opponent
    if opp is None:
        return list(ctx.state.neutral) if ctx.virtual_opponent else []
    return [loc for loc in ctx.state.neutral if ctx.away_at(loc, opp) > 0]


@operation("1SIS10", 0, uses=[A.DISCARD, A.SEND_AWAY_TEAM], cost=[DiscardFromHand(2)])
def strategic_operations(ctx, actions):
    """PLAY: Discard 2 cards to send 2 [Away Team] to the same Location."""
    yield from actions.send_away_team(2, same_location=True)


@operation("1SIS10", 1, uses=[A.DISMISS],
           trigger=lambda ctx, ev: ev["kind"] == "would_attack" and ev["seat"] == ctx.me.seat)
def stand_guard(ctx, actions):
    """REACTION: When you would be attacked, dismiss this card to ignore the negative effect."""
    yield from actions.dismiss(ctx.this_card)
    return True


@operation("1SIS10", 2, uses=[A.ATTACK, A.REMOVE_AWAY_TEAM, A.GAIN_RESOURCE], requires=lambda ctx: bool(_targets(ctx)))
def clear_the_field(ctx, actions):
    """ATTACK ACTIVATION: Remove an opponent [Away Team] from a neutral Location. Gain 1 [Glory]. The Glory is gained
    even when the attack is ignored."""
    if (yield from actions.attack(removes_away_teams=True)):
        loc = yield from actions.pick_card("Remove an opponent Away Team from which neutral Location?", _targets(ctx))
        if loc and ctx.opponent is not None:
            yield from actions.remove_away_team(loc, ctx.opponent)
    yield from actions.gain_resource("glory", 1)
