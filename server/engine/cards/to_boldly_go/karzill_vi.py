"""2REB04 Karzill VI (Location, Development). Spec: resources/scans/to_boldly_go/cards/captains/rebner/2REB04.md"""

from engine.cards import development_cost, endgame, operation
from engine.ops import A, Condition, Spend

from ._util import is_suit

development_cost("2REB04", Spend(latinum=2), Condition(lambda ctx: ctx.track("military") >= 5, "have 5+ Military"))


@operation("2REB04", 0, uses=[A.TAKE_CONTROL])
def take_control(ctx, actions):
    """PLAY: Take control of this location."""
    yield from actions.take_control(ctx.this_card)


@operation("2REB04", 1, uses=[A.FREE_PLAY])
def shipyard(ctx, actions):
    """CONTROL: You may free play a Ship."""
    card = yield from actions.pick_card("Free play a Ship?", actions.free_play_candidates(lambda i: is_suit(i, "Ship")),
                                        optional=True, none_label="No")
    if card:
        yield from actions.free_play(card)


@operation("2REB04", 2, uses=[A.GAIN_RESOURCE])
def idle_hands(ctx, actions):
    """CLEAN-UP: For each unspent [Action], gain 1 [Dilithium] and 1 [Glory]."""
    n = ctx.me.actions
    if n > 0:
        yield from actions.gain_resource("dilithium", n)
        yield from actions.gain_resource("glory", n)


@endgame("2REB04")
def treasury(state, player):
    """ENDGAME: Score 1 [VP] for every 4 [Glory] you have."""
    return player.glory // 4
