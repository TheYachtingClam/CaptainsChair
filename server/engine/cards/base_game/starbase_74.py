"""1PIC07 Starbase 74 (Location, Development). Spec: resources/scans/base_game/cards/captains/picard/1PIC07.md"""

from engine.cards import development_cost, duty_slots, operation
from engine.ops import A, Spend

from ._util import is_suit, others_in_hand, take_control_of_this

development_cost("1PIC07", Spend(dilithium=2, latinum=1))
operation("1PIC07", 0, uses=[A.TAKE_CONTROL])(take_control_of_this)


@operation("1PIC07", 1, uses=[A.FIND, A.DISCARD, A.FREE_PLAY])
def refit(ctx, actions):
    """CONTROL: Find a Person. You may discard a different card to free play the found card."""
    person, _ = yield from actions.find(lambda i: is_suit(i, "Person"), "a Person")
    if person is None:
        return
    others = others_in_hand(ctx, lambda i: i.uid != person.uid)
    if others and actions.free_play_candidates(lambda i: i.uid == person.uid) and (
            yield from actions.may(f"Discard a different card to free play {ctx.name(person)}?")):
        yield from actions.discard(1, pred=lambda i: i.uid != person.uid)
        yield from actions.free_play(person)


@duty_slots("1PIC07")
def extra_officer(state, owner, inst):
    """PASSIVE: You may have an additional Person on duty."""
    return [None]
