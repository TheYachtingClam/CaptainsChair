"""1BUR08 Doctor Kovich (Person, Development). Spec: resources/scans/base_game/cards/captains/burnham/1BUR08.md"""

from engine.cards import development_cost, hand_size_modifier, operation
from engine.ops import A, EffectCost

from ._util import count_traits, is_suit

TRACKS = ("research", "influence", "military")


def _encounter(inst):
    return is_suit(inst, "Encounter")


def _has_encounter(ctx):
    me = ctx.me
    return any(_encounter(i) for zone in (me.hand, me.draw, me.discard, me.reserve) for i in zone)


def _find_and_log(ctx, actions):
    found, _ = yield from actions.find(_encounter, "an Encounter (cost)")
    if found:
        yield from actions.log(found)


development_cost("1BUR08", EffectCost(_has_encounter, _find_and_log, (A.FIND, A.LOG), "find an Encounter and log it"))


@operation("1BUR08", 0, uses=[A.DRAW, A.GAIN_SPECIALTY])
def analysis(ctx, actions):
    """PLAY: Draw a card. For each Anomaly you have in play, gain 1 [Research]. For each Ambassador you have in play,
    gain 1 [Influence]. For each Alien you have in play, gain 1 [Military]."""
    yield from actions.draw(1)
    for trait, track in (("Anomaly", "research"), ("Ambassador", "influence"), ("Alien", "military")):
        n = count_traits(ctx, trait)
        if n:
            yield from actions.gain_specialty(track, n)


@hand_size_modifier("1BUR08")
def larger_hand(state, owner, size):
    """PASSIVE: Increase your hand size by 1 for each of [Research]/[Influence]/[Military] you have at 5+."""
    return size + sum(1 for t in TRACKS if owner.tracks.get(t, 0) >= 5)
