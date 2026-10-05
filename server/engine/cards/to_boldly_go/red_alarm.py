"""2REB14 Red Alarm (Incident). Spec: resources/scans/to_boldly_go/cards/captains/rebner/2REB14.md"""

from engine.cards import operation
from engine.ops import A, EffectCost

from ._util import is_helmet, ships


def _recall_officer(ctx, actions):
    """Cost: recall one of your Duty Officers (its Helmet comes back too, KW-HELM-03)."""
    officer = yield from actions.pick_card("Recall which Duty Officer?", list(ctx.me.duty))
    yield from actions.recall(officer)


@operation("2REB14", 0, uses=[A.RECALL, A.RETURN_INCIDENT, A.SPEND, A.REFRESH, A.DRAW_FROM_DISCARD],
           cost=[EffectCost(lambda ctx: bool(ctx.me.duty), _recall_officer, (A.RECALL,), "recall a Duty Officer")])
def battle_stations(ctx, actions):
    """PLAY: Recall a Duty Officer to return this card. You may spend 1 [Dilithium] to either: refresh a Ship OR draw
    a Helmet from your Discard pile."""
    yield from actions.return_incident(ctx.this_card)
    tired = [s for s in ships(ctx) if s.exhausted]
    helmets = [i for i in ctx.me.discard if is_helmet(i)]
    options = ([("refresh", "Refresh a Ship")] if tired else []) + ([("helmet", "Draw a Helmet")] if helmets else [])
    if not options or not actions.can_spend(dilithium=1):
        return
    choice = yield from actions.choose("Spend 1 Dilithium to:", options + [("none", "Neither")])
    if choice == "none":
        return
    yield from actions.spend(dilithium=1)
    if choice == "refresh":
        ship = yield from actions.pick_card("Refresh which Ship?", tired)
        yield from actions.refresh(ship)
    else:
        yield from actions.draw_from_discard(is_helmet, "a Helmet")
