"""Riker's Crew board missions. Specs: resources/scans/second_contact/boards/cb-riker-basic.md and
cb-riker-advanced.md."""

from engine.cards import mission_goal, mission_reward
from engine.ops import SPECIES, A

from ._util import has_trait


def _pakled_criteria(ctx):
    return [any(has_trait(i, "Pakled") for i in ctx.me.log), ctx.track("military") >= 8, ctx.track("influence") >= 4]


@mission_goal("battling-the-pakled")
def pakled_goal(ctx):
    """At least 2 of: a Pakled card in your Log; [Military] 8+; [Influence] 4+."""
    return [] if sum(_pakled_criteria(ctx)) >= 2 else None


@mission_reward("battling-the-pakled", uses=[A.GAIN_RESOURCE, A.SEND_AWAY_TEAM])
def pakled_reward(ctx, actions):
    """Gain 3 [Dilithium]/[Latinum] in any combination. Up to twice, send an [Away Team] to a Location. If you meet all
    3 criteria, gain 2 [Glory]."""
    all_three = all(_pakled_criteria(ctx))
    for n in (1, 2, 3):
        kind = yield from actions.choose(f"Gain which resource ({n} of 3)?", [("dilithium", "Dilithium"),
                                                                             ("latinum", "Latinum")])
        yield from actions.gain_resource(kind, 1)
    for n in (1, 2):
        if not (yield from actions.may(f"Send an Away Team to a Location ({n} of up to 2)?")):
            break
        yield from actions.send_away_team(1)
    if all_three:
        yield from actions.gain_resource("glory", 2)


@mission_goal("spirit-of-starfleet")
def spirit_goal(ctx):
    """Have a Starfleet Duty Officer, and 5 cards with [Research]/[Any Skill] in play (excluding beamed cards)."""
    officer = next((i for i in ctx.me.duty if has_trait(i, "Starfleet")), None)
    research = [i for i in ctx.in_play(beamed=False) if {"Research", "Any"} & set(ctx.skills(i))]
    return [officer, *research[:5]] if officer is not None and len(research) >= 5 else None


@mission_reward("spirit-of-starfleet", uses=[A.GAIN_ACTION, A.SCAN_FOR])
def spirit_reward(ctx, actions):
    """Gain an [Action]. Name a species, then scan for it."""
    yield from actions.gain_action(1)
    species = yield from actions.choose("Name a species.", [(s, s) for s in sorted(SPECIES)])
    yield from actions.scan_for(lambda i: has_trait(i, species), f"a {species}")


OLD_FRIENDS = ("Klingon", "Pilot", "Doctor", "Scientist", "Synthetic")


@mission_goal("messages-from-old-friends")
def old_friends_goal(ctx):
    """Have 4 of the following traits in play: Klingon, Pilot, Doctor, Scientist, Synthetic."""
    cards = ctx.in_play()
    shown = [t for t in OLD_FRIENDS if any(has_trait(i, t) for i in cards)]
    return [] if len(shown) >= 4 else None


@mission_reward("messages-from-old-friends", uses=[A.REFRESH, A.TAKE_ENCOUNTER])
def old_friends_reward(ctx, actions):
    """Refresh your Captain. Take the bottom Encounter."""
    if ctx.me.captain.exhausted:
        yield from actions.refresh(ctx.me.captain)
    yield from actions.take_encounter(bottom=True)
