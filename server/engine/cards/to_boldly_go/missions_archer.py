"""Archer's Crew board missions. Specs: resources/scans/to_boldly_go/boards/cb-archer-basic.md and
cb-archer-advanced.md."""

from engine.cards import mission_goal, mission_reward
from engine.ops import SPECIES, A

from ._util import count_traits, distinct_traits, has_trait, is_suit, ships


def _nx01(ctx):
    return next((s for s in ctx.me.fleet if s.card == "2ARC03"), None)


@mission_goal("history-with-every-light-year")
def history_goal(ctx):
    """Have the NX-01 Enterprise and an [Away Team] at a secured neutral Location. Have 1 Person on the NX-01
    Enterprise and at least 4 [Dilithium]."""
    nx = _nx01(ctx)
    if nx is None or ctx.me.dilithium < 4:
        return None
    loc = ctx.location_of(nx)
    person = next((b for b in nx.beamed if is_suit(b, "Person")), None)
    if loc in ctx.state.neutral and ctx.away_at(loc) and ctx.secured_by(loc) and person is not None:
        return [nx, person]
    return None


@mission_reward("history-with-every-light-year", uses=[A.SPEND, A.TAKE_CONTROL, A.FIND])
def history_reward(ctx, actions):
    """You may spend 4 [Dilithium] to take control of the NX-01 Enterprise's Location. You may find either Inspire or
    Strength of the Soul."""
    nx = _nx01(ctx)
    loc = ctx.location_of(nx) if nx else None
    if loc is not None and loc in ctx.state.neutral and actions.can_spend(dilithium=4) and (
            yield from actions.may(f"Spend 4 Dilithium to take control of {ctx.name(loc)}?")):
        yield from actions.spend(dilithium=4)
        yield from actions.take_control(loc)
    if (yield from actions.may("Find Inspire or Strength of the Soul?")):
        yield from actions.find(lambda i: ctx.name(i) in ("Inspire", "Strength of the Soul"),
                                "Inspire or Strength of the Soul", optional=True)


@mission_goal("coalition-of-planets")
def coalition_goal(ctx):
    """Have an Andorian, a Vulcan, and a Tellarite at the same controlled Location, and a Communication in play."""
    if not count_traits(ctx, "Communication"):
        return None
    for loc in ctx.me.locations:
        here = [loc, *loc.beamed]
        for ship in ctx.ships_at(loc):
            here += [ship, *ship.beamed]
        picks = []
        for trait in ("Andorian", "Vulcan", "Tellarite"):
            found = next((c for c in here if has_trait(c, trait) and c not in picks), None)
            if found is None:
                break
            picks.append(found)
        else:
            return picks
    return None


@mission_reward("coalition-of-planets", uses=[A.SCAN, A.DRAW, A.DESTROY, A.GAIN_RESOURCE])
def coalition_reward(ctx, actions):
    """Scan 2 of Person OR scan 1 of Ally. Draw a card. You may destroy a Romulan from your Discard pile to gain 3
    [Glory]."""
    choice = yield from actions.choose("Scan 2 of Person or 1 of Ally?", [("person", "Scan 2 of Person"),
                                                                          ("ally", "Scan 1 of Ally")])
    yield from actions.scan(2, ["Person"]) if choice == "person" else actions.scan(1, ["Ally"])
    yield from actions.draw(1)
    romulans = [i for i in ctx.me.discard if has_trait(i, "Romulan")]
    card = yield from actions.pick_card("Destroy a Romulan from your Discard pile to gain 3 Glory?", romulans,
                                        optional=True, none_label="No")
    if card:
        yield from actions.destroy(card)
        yield from actions.gain_resource("glory", 3)


@mission_goal("temporal-cold-war")
def cold_war_goal(ctx):
    """Have 5 Different Species (excluding Human), 2 Time Travel, and an Incident in play."""
    cards = ctx.in_play()
    species = distinct_traits(cards, SPECIES - {"Human"})
    tt = [i for i in cards if has_trait(i, "Time Travel")]
    incidents = [i for i in cards if is_suit(i, "Incident")]
    return [*tt[:2], incidents[0]] if species >= 5 and len(tt) >= 2 and incidents else None


@mission_reward("temporal-cold-war", uses=[A.GAIN_ACTION, A.LOG])
def cold_war_reward(ctx, actions):
    """Gain an [Action]. You may log a deployed Ship to gain an (additional) [Action]."""
    yield from actions.gain_action(1)
    ship = yield from actions.pick_card("Log a deployed Ship to gain another Action?", ships(ctx), optional=True,
                                        none_label="No")
    if ship:
        yield from actions.log(ship)
        yield from actions.gain_action(1)
