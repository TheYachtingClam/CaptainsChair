"""Kirk's Crew board missions. Specs: resources/scans/to_boldly_go/boards/cb-kirk-basic.md and cb-kirk-advanced.md."""

from engine.cards import mission_goal, mission_reward
from engine.ops import SPECIES, A

from ._util import has_trait, is_suit, ships


@mission_goal("where-no-man-has-gone-before")
def explore_goal(ctx):
    """Have 2 Encounter on the same Ship, and [Research] at 4+."""
    if ctx.track("research") < 4:
        return None
    for ship in ships(ctx):
        encounters = [c for c in [ship, *ship.beamed] if is_suit(c, "Encounter")]
        if len(encounters) >= 2:
            return encounters[:2]
    return None


@mission_reward("where-no-man-has-gone-before", uses=[A.TAKE_ENCOUNTER, A.REMOVE_STARDATE_GLORY])
def explore_reward(ctx, actions):
    """Take the top Encounter. Remove 2 [Glory] from the Stardate card."""
    yield from actions.take_encounter()
    yield from actions.remove_stardate_glory(2)


@mission_goal("the-undiscovered-country")
def country_goal(ctx):
    """Have 3 of the same Any Species (excluding cards with Human / Starfleet) in play, and [Influence] at 4+."""
    if ctx.track("influence") < 4:
        return None
    cards = [i for i in ctx.in_play() if not has_trait(i, "Human", "Starfleet")]
    for species in sorted(SPECIES):
        same = [i for i in cards if has_trait(i, species)]
        if len(same) >= 3:
            return same[:3]
    return None


@mission_reward("the-undiscovered-country", uses=[A.ENLIST_DEVELOPMENT])
def country_reward(ctx, actions):
    """Enlist a Development for free."""
    yield from actions.enlist_development(free=True)


@mission_goal("search-for-spock")
def spock_goal(ctx):
    """Have Captain Spock logged, the H.M.S. Bounty in play, 5 Person in play, and [Military] at 4+."""
    spock = next((i for i in ctx.me.log if i.card == "2KIRK24"), None)
    bounty = next((i for i in ctx.in_play() if i.card == "2KIRK11"), None)
    people = [i for i in ctx.in_play() if is_suit(i, "Person")]
    if spock and bounty and len(people) >= 5 and ctx.track("military") >= 4:
        return [bounty, *people[:5]]
    return None


@mission_reward("search-for-spock", uses=[A.DRAW_FROM_LOG, A.FREE_PLAY, A.FIND, A.RETURN_INCIDENT, A.GAIN_ACTION,
                                          A.DISMISS])
def spock_reward(ctx, actions):
    """Draw Captain Spock from your Log, and you may free play Captain Spock. You may find an Incident and return it.
    Gain an [Action]. Dismiss the H.M.S. Bounty."""
    spock = yield from actions.draw_from_log(lambda i: i.card == "2KIRK24", "Captain Spock")
    if spock and actions.free_play_candidates(lambda i: i is spock) and (yield from actions.may("Free play Captain Spock?")):
        yield from actions.free_play(spock)
    if (yield from actions.may("Find an Incident and return it?")):
        incident, _ = yield from actions.find(lambda i: is_suit(i, "Incident"), "an Incident", optional=True)
        if incident:
            yield from actions.return_incident(incident)
    yield from actions.gain_action(1)
    bounty = next((i for i in [*ctx.me.fleet, *ctx.me.duty] if i.card == "2KIRK11"), None)
    if bounty:
        yield from actions.dismiss(bounty)
