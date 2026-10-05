"""3RIK25 The Riker Maneuver (Directive). Spec: resources/scans/second_contact/cards/captains/william riker/3RIK25.md"""

from engine.cards import operation
from engine.ops import A, DismissDutyOfficer

from ._util import is_suit


@operation("3RIK25", 0, uses=[A.DISMISS, A.SEND_AWAY_TEAM, A.EXHAUST, A.PROMOTE], cost=[DismissDutyOfficer()])
def maneuver(ctx, actions):
    """PLAY: Dismiss a Duty Officer to send an [Away Team] to a Location. You may exhaust your Captain to promote this
    card to Duty Officer as if it is a Person, then exhaust this card."""
    yield from actions.send_away_team(1)
    me = ctx.this_card
    if me in ctx.me.staging and not ctx.me.captain.exhausted and (
            yield from actions.may("Exhaust your Captain to promote The Riker Maneuver to Duty Officer?")):
        yield from actions.exhaust(ctx.me.captain)
        yield from actions.promote(me, as_person=True)
        if me in ctx.me.duty:
            yield from actions.exhaust(me)


@operation("3RIK25", 1, uses=[A.GAIN_RESOURCE, A.FREE_PLAY, A.PROMOTE, A.DISMISS])
def command_decision(ctx, actions):
    """ACTIVATION: Choose up to 2 of the following: gain 2 [Latinum] OR free play a Directive/Person OR promote a
    Person from your hand to Duty Officer. Dismiss this card."""
    done: set[str] = set()
    for n in (1, 2):
        plays = actions.free_play_candidates(lambda i: is_suit(i, "Directive", "Person") and i is not ctx.this_card)
        people = [i for i in ctx.me.hand if is_suit(i, "Person")]
        options = [(k, label) for k, label, ok in (("latinum", "Gain 2 Latinum", True),
                                                   ("play", "Free play a Directive or Person", bool(plays)),
                                                   ("promote", "Promote a Person from your hand", bool(people)))
                   if ok and k not in done]
        choice = yield from actions.choose(f"Choose an option ({n} of up to 2).", options + [("stop", "Stop")])
        if choice == "stop":
            break
        done.add(choice)
        if choice == "latinum":
            yield from actions.gain_resource("latinum", 2)
        elif choice == "play":
            card = yield from actions.pick_card("Free play which card?", plays)
            yield from actions.free_play(card)
        else:
            person = yield from actions.pick_card("Promote which Person?", people)
            yield from actions.promote(person)
    yield from actions.dismiss(ctx.this_card)


