"""2KHA08 Ceti Eel (Cargo, Development). Spec: resources/scans/to_boldly_go/cards/captains/kahn/2KHA08.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import virtual

development_cost("2KHA08", Spend(dilithium=1, latinum=1))


def _has_duty_officer(ctx):
    return virtual(ctx) or (ctx.opponent is not None and bool(ctx.opponent.duty))


def _contested(ctx, loc):
    """A neutral Location where either of you has a token. The virtual opponent has an Away Team at each."""
    if loc not in ctx.state.neutral:
        return False
    opp = ctx.opponent
    theirs = virtual(ctx) or (opp is not None and (ctx.away_at(loc, opp) or ctx.ships_at(loc, opp)))
    return bool(ctx.away_at(loc) or ctx.ships_at(loc) or theirs)


@operation("2KHA08", 0, uses=[A.ATTACK, A.DISMISS, A.SEND_AWAY_TEAM, A.PUT, A.DRAW, A.FORCE], requires=_has_duty_officer)
def mind_control(ctx, actions):
    """ATTACK PLAY: Dismiss an opponent Duty Officer to send 2 [Away Team] to a neutral Location where either of you
    has a token, ignoring any opponent Ship. Put this card back in your Development pile. Your opponent may draw 2
    cards. If the attack is ignored, no Duty Officer is dismissed and no Away Teams are sent."""
    opp = ctx.opponent
    if (yield from actions.attack()):
        if opp is not None and opp.duty:
            officer = yield from actions.pick_card("Dismiss which opponent Duty Officer?", list(opp.duty))
            yield from actions.dismiss(officer)
        yield from actions.send_away_team(2, where=lambda loc: _contested(ctx, loc), same_location=True,
                                          ignore_ships=True)
    yield from actions.put_in_development(ctx.this_card)
    if opp is not None and (yield from actions.may("Draw 2 cards (Ceti Eel)?", seat=opp.seat)):
        yield from actions.draw(2, player=opp)


@operation("2KHA08", 1, uses=[A.FIND, A.LOG, A.RETURN_INCIDENT])
def burrow(ctx, actions):
    """PLAY: Find any card and log the found card. You may return an Incident. Log this card."""
    found, _ = yield from actions.find(lambda i: True, "any card")
    if found is not None:
        yield from actions.log(found)
    incident = yield from actions.pick_card("Return an Incident?", ctx.hand_incidents(), optional=True, none_label="No")
    if incident is not None:
        yield from actions.return_incident(incident)
    yield from actions.log(ctx.this_card)
