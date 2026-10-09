"""1SHR20 Talas (Person). Spec: resources/scans/base_game/cards/captains/shran/1SHR20.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

RIVALS = ("Vulcan", "Tellarite", "Romulan")


@operation("1SHR20", 0, uses=[A.SEND_AWAY_TEAM, A.ATTACK, A.DISMISS])
def tactical(ctx, actions):
    """ATTACK PLAY: Send an [Away Team] to a Location. Dismiss an opponent Vulcan/Tellarite/Romulan (of your choice).
    A card in their Staging Area cannot be dismissed (KW-DSM-04)."""
    yield from actions.send_away_team(1)
    opp = ctx.opponent
    if not (yield from actions.attack()) or opp is None:
        return
    targets = [i for i in ctx.in_play(opp) if i not in opp.staging and i is not opp.captain
               and ctx.traits(i) & set(RIVALS)]
    target = yield from actions.pick_card("Dismiss which opponent Vulcan, Tellarite or Romulan?", targets)
    if target:
        yield from actions.dismiss(target)


@operation("1SHR20", 1, uses=[A.DISCARD, A.SEND_AWAY_TEAM], cost=[DiscardFromHand(2)])
def deploy_guard(ctx, actions):
    """ACTIVATION: Discard 2 cards to send an [Away Team] to a Location."""
    yield from actions.send_away_team(1)
