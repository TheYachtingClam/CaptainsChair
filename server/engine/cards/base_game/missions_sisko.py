"""Sisko's Crew board missions. Specs: resources/scans/base_game/boards/cb-sisko-basic.md and cb-sisko-advanced.md.
A goal returns the cards that meet it; beamed ones are dismissed on completion (REQ-MS-06)."""

from engine.cards import mission_goal, mission_reward
from engine.ops import A

from ._util import count_traits, has_trait, location_of_player, ships

BAJOR = "1SIS02"


@mission_goal("a-call-to-arms")
def arms_goal(ctx):
    """Have 4 Ship deployed. Have [Influence] at 7+ OR [Military] at 7+."""
    fleet = ships(ctx)
    return fleet[:4] if len(fleet) >= 4 and (ctx.track("influence") >= 7 or ctx.track("military") >= 7) else None


@mission_reward("a-call-to-arms", uses=[A.ENLIST_DEVELOPMENT])
def arms_reward(ctx, actions):
    """Enlist a Development, reducing the cost by 1 [Dilithium] or 1 [Latinum] for each Starbase you have in play."""
    yield from actions.enlist_development(discount=count_traits(ctx, "Starbase"))


@mission_goal("bajors-application-to-the-federation")
def application_goal(ctx):
    """Have 2 Starfleet (excluding your Captain) and 3 Bajoran in play. Have a Ship at Bajor."""
    cards = ctx.in_play()
    starfleet = [i for i in cards if i is not ctx.me.captain and has_trait(i, "Starfleet")]
    bajoran = [i for i in cards if has_trait(i, "Bajoran")]
    bajor = location_of_player(ctx.me, BAJOR)
    if bajor is None or not ctx.ships_at(bajor) or len(starfleet) < 2 or len(bajoran) < 3:
        return None
    return [*starfleet[:2], *bajoran[:3]]


@mission_reward("bajors-application-to-the-federation", uses=[A.TRIGGER_CONTROL, A.REFRESH])
def application_reward(ctx, actions):
    """Trigger the control operation of one of your controlled Location. Refresh Bajor."""
    loc = yield from actions.pick_card("Trigger the CONTROL of which Location?", ctx.controlled_locations())
    if loc:
        yield from actions.trigger_control(loc)
    bajor = location_of_player(ctx.me, BAJOR)
    if bajor is not None and bajor.exhausted:
        yield from actions.refresh(bajor)


@mission_goal("contacting-the-dominion")
def dominion_goal(ctx):
    """Have 3 Dominion / Changeling in play."""
    found = [i for i in ctx.in_play() if has_trait(i, "Dominion", "Changeling")]
    return found[:3] if len(found) >= 3 else None


@mission_reward("contacting-the-dominion", uses=[A.GAIN_SPECIALTY, A.SCAN, A.DRAW])
def dominion_reward(ctx, actions):
    """Gain 3 [Influence]. Scan 1 of either Person, Cargo, or Ship. Draw 2 cards."""
    yield from actions.gain_specialty("influence", 3)
    yield from actions.scan(1, ["Person", "Cargo", "Ship"])
    yield from actions.draw(2)
