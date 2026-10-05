"""2REB09 Rumdar (Person). Spec: resources/scans/to_boldly_go/cards/captains/rebner/2REB09.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, wearing


@operation("2REB09", 0, uses=[A.SEND_AWAY_TEAM, A.ATTACK, A.FORCE, A.DISCARD, A.DISMISS, A.GAIN_RESOURCE])
def infiltrate(ctx, actions):
    """ATTACK PLAY: Send an [Away Team] to a neutral Location. Force your opponent to discard a card. You may dismiss
    an opponent Spy to gain 1 [Glory]. Cadet: the virtual opponent's Spy is dismissed for the Glory (REQ-CTM-12)."""
    yield from actions.send_away_team(1, where=lambda loc: loc in ctx.state.neutral)
    if not (yield from actions.attack()):
        return
    opp = ctx.opponent
    if opp is None:
        if ctx.virtual_opponent and (yield from actions.may("Dismiss the virtual opponent's Spy to gain 1 Glory?")):
            yield from actions.gain_resource("glory", 1)
        return
    yield from actions.discard(1, player=opp)
    table = [i for i in ctx.in_play(opp) if i not in opp.staging]
    spies = [i for i in table if has_trait(i, "Spy")]
    spy = yield from actions.pick_card("Dismiss an opponent Spy to gain 1 Glory?", spies, optional=True,
                                       none_label="No")
    if spy:
        yield from actions.dismiss(spy)
        yield from actions.gain_resource("glory", 1)


@operation("2REB09", 1, uses=[A.DRAW, A.TAKE_INCIDENT, A.ENLIST_DEVELOPMENT],
           trigger=lambda ctx, ev: ev["kind"] == "draw" and ev["seat"] == ctx.me.seat
           and ev.get("source") == ctx.me.captain.uid and ctx.me.captain.card == "2REB01")
def double_down(ctx, actions):
    """REACTION: After drawing cards due to Rebner's operations, draw 2 cards. If Rumdar is wearing a Helmet, you may
    take an Incident to enlist a Development."""
    yield from actions.draw(2)
    if wearing(ctx.this_card) and ctx.state.incident and (
            yield from actions.may("Take an Incident to enlist a Development?")):
        yield from actions.take_incident()
        yield from actions.enlist_development()
