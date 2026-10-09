"""1SHR19 Ushaan-Tor (Cargo). Spec: resources/scans/base_game/cards/captains/shran/1SHR19.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import has_trait


@operation("1SHR19", 0, uses=[A.DISCARD, A.GAIN_RESOURCE, A.ATTACK, A.FORCE, A.DISMISS],
           cost=[DiscardFromHand(1, lambda ctx, i: has_trait(i, "Andorian"), "an Andorian")])
def duel(ctx, actions):
    """ATTACK PLAY: Discard an Andorian to gain 1 [Glory] and to force your opponent to dismiss (one of) their Duty
    Officer(s)."""
    yield from actions.gain_resource("glory", 1)
    opp = ctx.opponent
    if (yield from actions.attack()) and opp is not None and opp.duty:
        officer = yield from actions.pick_card("Ushaan-Tor: dismiss one of your Duty Officers.", list(opp.duty),
                                               seat=opp.seat)
        yield from actions.dismiss(officer)
