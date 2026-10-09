"""Sela's Crew board missions. Specs: resources/scans/base_game/boards/cb-sela-basic.md and cb-sela-advanced.md.
A goal returns the cards that meet it; beamed ones are dismissed on completion (REQ-MS-06)."""

from engine.cards import mission_goal, mission_reward
from engine.ops import A

from ._util import count_traits, has_trait, is_suit, ships


@mission_goal("romulan-might")
def might_goal(ctx):
    """Have [Influence] at 6+ and [Military] at 6+."""
    return [] if ctx.track("influence") >= 6 and ctx.track("military") >= 6 else None


@mission_reward("romulan-might", uses=[A.ENLIST_DEVELOPMENT, A.FIND])
def might_reward(ctx, actions):
    """Enlist a Development. Find an Attack."""
    yield from actions.enlist_development()
    yield from actions.find(lambda i: has_trait(i, "Attack"), "an Attack")


@mission_goal("the-reunification-plot")
def reunification_goal(ctx):
    """Have 4 Vulcan in play."""
    vulcans = [i for i in ctx.in_play() if has_trait(i, "Vulcan")]
    return vulcans[:4] if len(vulcans) >= 4 else None


@mission_reward("the-reunification-plot", uses=[A.GAIN_SPECIALTY, A.DRAW, A.FREE_PLAY, A.JUNK])
def reunification_reward(ctx, actions):
    """Gain 3 [Influence]. Draw a card for each Shady you have in play. You may free play an Incident. You may junk a
    card from the Market."""
    yield from actions.gain_specialty("influence", 3)
    shady = count_traits(ctx, "Shady")
    if shady:
        yield from actions.draw(shady)
    incidents = actions.free_play_candidates(lambda i: is_suit(i, "Incident"))
    incident = yield from actions.pick_card("Free play an Incident?", incidents, optional=True, none_label="No")
    if incident:
        yield from actions.free_play(incident)
    if (yield from actions.may("Junk a card from the Market?")):
        yield from actions.junk()


@mission_goal("the-duras-plot")
def duras_goal(ctx):
    """Have 1+ Klingon on the same Ship that has Cloak."""
    for ship in ships(ctx):
        klingon = next((b for b in ship.beamed if has_trait(b, "Klingon")), None)
        if klingon is not None and has_trait(ship, "Cloak"):
            return [ship, klingon]
    return None


@mission_reward("the-duras-plot", uses=[A.GAIN_SPECIALTY, A.GAIN_RESOURCE, A.DISMISS])
def duras_reward(ctx, actions):
    """Gain 1 [Military] for each Cloak in play. Gain 2 [Glory] from the supply (not the Stardate card) for each
    Klingon in play. Dismiss one Cloak and all beamed Klingon."""
    cloaks = count_traits(ctx, "Cloak")
    if cloaks:
        yield from actions.gain_specialty("military", cloaks)
    klingons = count_traits(ctx, "Klingon")
    if klingons:
        yield from actions.gain_resource("glory", 2 * klingons, supply=True)
    mine = [i for i in ctx.in_play() if i not in ctx.me.staging and has_trait(i, "Cloak")]
    cloak = yield from actions.pick_card("Dismiss which Cloak?", mine)
    if cloak:
        yield from actions.dismiss(cloak)
    for host in ctx.in_play(beamed=False):
        for klingon in [b for b in host.beamed if has_trait(b, "Klingon")]:
            yield from actions.dismiss(klingon)
