"""1KOL21 Arne Darvin (Person). Spec: resources/scans/base_game/cards/captains/koloth/1KOL21.md"""

from engine.cards import hand_size_modifier, operation
from engine.ops import A


@operation("1KOL21", 0, uses=[A.GAIN_RESOURCE, A.ATTACK, A.STEAL])
def pilfer(ctx, actions):
    """ATTACK PLAY: Gain 1 [Dilithium] and steal 1 [Dilithium]."""
    yield from actions.gain_resource("dilithium", 1)
    if (yield from actions.attack()):
        yield from actions.steal("dilithium", 1)


@operation("1KOL21", 1, uses=[A.ATTACK, A.FORCE, A.DISMISS, A.TAKE_INCIDENT, A.GAIN_RESOURCE, A.LOG],
           requires=lambda ctx: ctx.track("influence") >= 4)
def unmasked(ctx, actions):
    """ATTACK PLAY: Requires [Influence] 4. Force your opponent to dismiss a Duty Officer. You take 1 Incident and gain
    3 [Glory] and log this card."""
    opp = ctx.opponent
    if (yield from actions.attack()) and opp is not None and opp.duty:
        officer = yield from actions.pick_card("Arne Darvin: dismiss one of your Duty Officers.", list(opp.duty),
                                               seat=opp.seat)
        yield from actions.dismiss(officer)
    yield from actions.take_incident()
    yield from actions.gain_resource("glory", 3)
    yield from actions.log(ctx.this_card)


@hand_size_modifier("1KOL21")
def larger_hand(state, owner, size):
    """PASSIVE: Increase your hand size by 1."""
    return size + 1
