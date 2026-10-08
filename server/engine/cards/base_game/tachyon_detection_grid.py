"""1CAR13 Tachyon Detection Grid (Cargo). Spec: resources/scans/base_game/cards/cargo/1CAR13.md"""

from engine.cards import operation
from engine.ops import A

from ._util import count_traits, ships


@operation("1CAR13", 0, uses=[A.DISMISS, A.GAIN_SPECIALTY, A.ATTACK, A.FORCE, A.LOG, A.GAIN_RESOURCE])
def sweep(ctx, actions):
    """ATTACK PLAY: You may dismiss a deployed Ship to gain 2 [Research]. Force your opponent to log a Cloak from play.
    If they do, you gain 1 [Glory]. If you have a Security in play, gain 1 [Military].
    Cadet Training: the virtual opponent has one Cloak, so you gain the Glory (REQ-CTM-12)."""
    ship = yield from actions.pick_card("Dismiss a deployed Ship to gain 2 Research?", ships(ctx), optional=True,
                                        none_label="No")
    if ship:
        yield from actions.dismiss(ship)
        yield from actions.gain_specialty("research", 2)
    if (yield from actions.attack()):
        opp = ctx.opponent
        if opp is None:
            if ctx.virtual_opponent:
                yield from actions.gain_resource("glory", 1)
        else:
            cloaks = [i for i in ctx.in_play(opp) if "Cloak" in ctx.traits(i) and i not in opp.staging]
            if cloaks:
                cloak = yield from actions.pick_card("Tachyon Detection Grid: log one of your Cloak cards.", cloaks,
                                                     seat=opp.seat)
                yield from actions.log(cloak)
                yield from actions.gain_resource("glory", 1)
    if count_traits(ctx, "Security"):
        yield from actions.gain_specialty("military", 1)
