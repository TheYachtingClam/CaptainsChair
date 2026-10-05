"""Pike's Crew board missions. Specs: resources/scans/second_contact/boards/cb-pike-basic.md and
cb-pike-advanced.md."""

from engine.cards import mission_goal, mission_reward
from engine.ops import A

from ._util import has_trait, is_suit


@mission_goal("weight-of-the-future")
def weight_goal(ctx):
    """Have 4 Time Travel in play (excluding your Captain) and 2 deployed Ongoing."""
    tt = [i for i in ctx.in_play() if i is not ctx.me.captain and has_trait(i, "Time Travel")]
    ongoing = [i for i in ctx.me.fleet if has_trait(i, "Ongoing")]
    return [*tt[:4], *ongoing[:2]] if len(tt) >= 4 and len(ongoing) >= 2 else None


@mission_reward("weight-of-the-future", uses=[A.RETURN_INCIDENT, A.DRAW])
def weight_reward(ctx, actions):
    """Up to twice, return an Incident from your hand, Discard pile, or Log. For each Incident returned this way,
    draw a card."""
    for n in (1, 2):
        incidents = [i for i in ctx.me.hand + ctx.me.discard + ctx.me.log if is_suit(i, "Incident")]
        incident = yield from actions.pick_card(f"Return an Incident ({n} of up to 2)?", incidents, optional=True,
                                                none_label="Stop")
        if not incident:
            break
        yield from actions.return_incident(incident)
        yield from actions.draw(1)


@mission_goal("boy-scout")
def boy_scout_goal(ctx):
    """Have 7 Person in play, and [Influence] at 7+."""
    people = [i for i in ctx.in_play() if is_suit(i, "Person")]
    return people[:7] if len(people) >= 7 and ctx.track("influence") >= 7 else None


@mission_reward("boy-scout", uses=[A.SCAN, A.REFRESH])
def boy_scout_reward(ctx, actions):
    """Scan 2 of Ally. Refresh a card for each non-Starfleet Person you have in play."""
    yield from actions.scan(2, ["Ally"])
    n = sum(1 for i in ctx.in_play() if is_suit(i, "Person") and not has_trait(i, "Starfleet"))
    for k in range(1, n + 1):
        tired = [i for i in [ctx.me.captain, *ctx.me.status, *ctx.me.fleet, *ctx.me.locations, *ctx.me.duty]
                 if i.exhausted]
        card = yield from actions.pick_card(f"Refresh a card ({k} of {n})?", tired)
        if not card:
            break
        yield from actions.refresh(card)


def _explore_location(ctx):
    for loc in ctx.state.neutral:
        here = []
        for ship in ctx.ships_at(loc):
            here += [ship, *ship.beamed]
        here += loc.beamed
        starfleet = [c for c in here if has_trait(c, "Starfleet")]
        other = [c for c in here if has_trait(c, "Alien", "Anomaly") and c not in starfleet[:3]]
        if len(starfleet) >= 3 and other:
            return loc, [*starfleet[:3], other[0]]
    return None, None


@mission_goal("to-explore")
def explore_goal(ctx):
    """Have 2 Encounter in play, and have 3 Starfleet and an Alien/Anomaly at the same neutral Location."""
    encounters = [i for i in ctx.in_play() if is_suit(i, "Encounter")]
    _, cards = _explore_location(ctx)
    return [*encounters[:2], *cards] if len(encounters) >= 2 and cards else None


@mission_reward("to-explore", uses=[A.TAKE_CONTROL, A.REMOVE_STARDATE_GLORY])
def explore_reward(ctx, actions):
    """Take control of the Location used to fulfill the goal. Remove 1 [Glory] from the Stardate card."""
    loc, _ = _explore_location(ctx)
    if loc is not None:
        yield from actions.take_control(loc)
    yield from actions.remove_stardate_glory(1)
