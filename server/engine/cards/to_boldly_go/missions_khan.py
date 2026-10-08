"""Khan's Crew board missions. Spec: resources/scans/to_boldly_go/boards/cb-khan.md
The goals count the traits marked on the board (REQ-CD-KHN-06); no card contributes, so none is dismissed."""

from engine.cards import mission_goal, mission_reward
from engine.ops import A

from ._util import is_suit


@mission_goal("ive-hurt-you")
def hurt_goal(ctx):
    """Have 6 traits marked."""
    return [] if ctx.traits_marked() >= 6 else None


@mission_reward("ive-hurt-you", uses=[A.TAKE_ENCOUNTER])
def hurt_reward(ctx, actions):
    """Take the top Encounter."""
    yield from actions.take_encounter()


@mission_goal("i-shall-leave-you-as-you-left-me")
def leave_goal(ctx):
    """Have 9 traits marked."""
    return [] if ctx.traits_marked() >= 9 else None


@mission_reward("i-shall-leave-you-as-you-left-me", uses=[A.TAKE_ENCOUNTER, A.FLIP_CARD])
def leave_reward(ctx, actions):
    """Look at the top 2 Encounter, take one of them and return the other to the bottom of its deck. Flip your
    Captain card. This is the only thing that flips Khan's Captain."""
    yield from actions.take_encounter(look=2)
    yield from actions.flip(ctx.me.captain)


@mission_goal("marooned-for-all-eternity")
def marooned_goal(ctx):
    """Have all 12 traits marked."""
    return [] if ctx.traits_marked() >= 12 else None


@mission_reward("marooned-for-all-eternity", uses=[A.ATTACK, A.FORCE, A.RECALL, A.LOG])
def marooned_reward(ctx, actions):
    """ATTACK REWARD: Force your opponent to recall a Person, if able, and log the recalled card. The Person is one
    of their Duty Officers or one beamed in their play."""
    opp = ctx.opponent
    if not (yield from actions.attack()) or opp is None:
        return
    people = [i for i in ctx.in_play(opp) if is_suit(i, "Person") and i not in opp.staging]
    person = yield from actions.pick_card("Marooned for All Eternity: recall one of your Persons (it is then logged).",
                                          people, seat=opp.seat)
    if person is not None:
        yield from actions.recall(person)
        yield from actions.log(person)
