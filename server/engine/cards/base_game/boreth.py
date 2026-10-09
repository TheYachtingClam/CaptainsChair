"""1KOL05 Boreth (Location, Development). Spec: resources/scans/base_game/cards/captains/koloth/1KOL05.md"""

from engine.cards import development_cost, endgame, operation
from engine.ops import A, Condition, DiscardFromHand, Spend

from ._util import ctx_for, non_time_travel_in_staging, take_control_of_this

development_cost("1KOL05", Spend(dilithium=6), Condition(lambda ctx: ctx.me.glory >= 10, "have 10+ Glory"))
operation("1KOL05", 0, uses=[A.TAKE_CONTROL])(take_control_of_this)


@operation("1KOL05", 1, uses=[A.FIND, A.FREE_PLAY])
def vision(ctx, actions):
    """CONTROL: Find any card and free play it."""
    found, _ = yield from actions.find(lambda i: True, "any card")
    if found is not None and actions.free_play_candidates(lambda i: i.uid == found.uid):
        yield from actions.free_play(found)


@operation("1KOL05", 2, uses=[A.DRAW], cost=[Spend(dilithium=1)], requires=lambda ctx: bool(ctx.me.draw))
def time_crystal(ctx, actions):
    """ACTIVATION: Spend 1 [Dilithium] to draw the bottom card of your deck."""
    yield from actions.draw(1, bottom=True)


@operation("1KOL05", 3, uses=[A.DISCARD, A.RECALL], cost=[Spend(dilithium=1), DiscardFromHand(1)],
           requires=lambda ctx: bool(non_time_travel_in_staging(ctx)))
def second_chance(ctx, actions):
    """ACTIVATION: Spend 1 [Dilithium] and discard a card to recall a non-Time Travel card from your Staging Area."""
    card = yield from actions.pick_card("Recall which card from your Staging Area?", non_time_travel_in_staging(ctx))
    if card:
        yield from actions.recall(card)


@endgame("1KOL05")
def mastery(state, player):
    """ENDGAME: Score 1 [VP] for each [Research]/[Influence]/[Military]/[Any Skill] you have in play (excluding beamed
    cards)."""
    ctx = ctx_for(state, player)
    return sum(len(ctx.skills(i)) for i in ctx.in_play(beamed=False))
