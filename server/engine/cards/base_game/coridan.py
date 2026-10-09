"""1SHR04 Coridan (Location, Development). Spec: resources/scans/base_game/cards/captains/shran/1SHR04.md"""

from engine.cards import development_cost, endgame, operation
from engine.ops import A, Spend

from ._util import others_in_hand, take_control_of_this

development_cost("1SHR04", Spend(dilithium=2, latinum=1))
operation("1SHR04", 0, uses=[A.TAKE_CONTROL])(take_control_of_this)


@operation("1SHR04", 1, uses=[A.DISCARD, A.GAIN_RESOURCE])
def mines(ctx, actions):
    """CONTROL: You may discard 2 cards to gain 2 [Dilithium] and 2 [Latinum]."""
    if len(others_in_hand(ctx)) >= 2 and (yield from actions.may("Discard 2 cards to gain 2 Dilithium and 2 Latinum?")):
        yield from actions.discard(2)
        yield from actions.gain_resource("dilithium", 2)
        yield from actions.gain_resource("latinum", 2)


@operation("1SHR04", 2, uses=[A.GAIN_RESOURCE])
def output(ctx, actions):
    """RESUPPLY: Gain 1 [Dilithium]. If you have 7+ [Influence], gain an additional 1 [Dilithium]."""
    yield from actions.gain_resource("dilithium", 2 if ctx.track("influence") >= 7 else 1)


@endgame("1SHR04")
def stockpile(state, player):
    """ENDGAME: Score 1 [VP] for every 4 [Dilithium] you have."""
    return player.dilithium // 4
