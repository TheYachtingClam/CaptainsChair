"""2ALL13 Tellarites (Ally). Spec: resources/scans/to_boldly_go/cards/ally/2ALL13.md"""

from engine.cards import operation
from engine.ops import A

from ._util import count_traits, is_suit, others_in_hand


@operation("2ALL13", 0, uses=[A.ATTACK, A.GIVE, A.GAIN_ACTION])
def argue(ctx, actions):
    """ATTACK PLAY: Give your opponent an Incident from your hand. If you have another Tellarite in play, gain an
    [Action]. Ruling: with no Incident in hand nothing is given (KW-GIVE-02); the action is still gained."""
    incidents = others_in_hand(ctx, lambda i: is_suit(i, "Incident"))
    if (yield from actions.attack()) and incidents:
        incident = yield from actions.pick_card("Give which Incident to your opponent?", incidents)
        yield from actions.give_incident(incident)
    if count_traits(ctx, "Tellarite", exclude=ctx.this_card):
        yield from actions.gain_action(1)
