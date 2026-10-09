"""1SHR09 Ambassador Thoris (Person, Development). Spec: resources/scans/base_game/cards/captains/shran/1SHR09.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import is_suit

development_cost("1SHR09", Spend(dilithium=2))


@operation("1SHR09", 0, uses=[A.RETURN_INCIDENT, A.FORCE, A.GAIN_RESOURCE])
def accord(ctx, actions):
    """PLAY: All players may return an Incident from their hand or Discard pile. For each Incident returned, gain 1
    [Glory]. The Bot declines (REQ-SOLO-111); the Cadet virtual opponent returns nothing."""
    returned = 0
    mine = yield from actions.pick_card("Return an Incident from your hand or Discard pile?",
                                        ctx.hand_incidents("discard"), optional=True, none_label="No")
    if mine:
        yield from actions.return_incident(mine)
        returned += 1
    opp = ctx.opponent
    if opp is not None and opp.bot is None:
        theirs = yield from actions.pick_card("Ambassador Thoris: return an Incident from your hand or Discard pile?",
                                              [i for i in opp.hand + opp.discard if is_suit(i, "Incident")],
                                              optional=True, seat=opp.seat, none_label="No")
        if theirs:
            yield from actions.return_incident(theirs, player=opp)
            returned += 1
    if returned:
        yield from actions.gain_resource("glory", returned)


@operation("1SHR09", 1, uses=[A.GAIN_RESOURCE])
def alliance(ctx, actions):
    """ACTIVATION: Gain 1 [Glory] for each Ally you have in play."""
    n = ctx.count_in_play(lambda i: is_suit(i, "Ally"))
    if n:
        yield from actions.gain_resource("glory", n)
