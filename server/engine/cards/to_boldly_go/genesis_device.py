"""2KHA11 Genesis Device (Cargo, Ongoing, Development). Spec: resources/scans/to_boldly_go/cards/captains/kahn/2KHA11.md"""

from engine.cards import development_cost, endgame, operation
from engine.ops import A, Condition, Spend

from ._util import completed_mission_vp

development_cost("2KHA11", Spend(dilithium=2, latinum=1),
                 Condition(lambda ctx: len(ctx.me.development) == 1, "have no other cards in your Development pile"))


@operation("2KHA11", 0, uses=[A.MARK_TRAIT, A.ATTACK, A.DESTROY, A.DEPLOY])
def detonate(ctx, actions):
    """ATTACK PLAY: Mark any one trait. Destroy a neutral Location. (No [Glory] compensation is given for removed
    tokens.) Deploy this card."""
    yield from actions.mark_trait()
    if ctx.state.neutral and (yield from actions.attack()):
        loc = yield from actions.pick_card("Destroy which neutral Location?", list(ctx.state.neutral))
        yield from actions.destroy(loc)
    yield from actions.deploy(ctx.this_card)


@endgame("2KHA11")
def life_from_lifelessness(state, player):
    """ENDGAME: Score the [VP] for all your completed Mission an additional time."""
    return completed_mission_vp(player)
