"""1PER09 Joret Dal (Person). Spec: resources/scans/base_game/cards/person/1PER09.md"""

from engine.cards import hand_size_modifier, operation
from engine.ops import A

from ._util import is_suit, people_in_hand


@operation("1PER09", 0, uses=[A.PUT, A.SEND_AWAY_TEAM, A.LOG, A.GAIN_RESOURCE, A.PROMOTE])
def defect(ctx, actions):
    """PLAY: You may put a Person on the top of your deck to send an [Away Team] to a Location. You may log a Person
    from your hand or Discard pile. If you do both, gain 1 [Glory] and you may promote this card to Duty Officer."""
    this = ctx.this_card
    sent = logged = False
    person = yield from actions.pick_card("Put a Person on top of your deck to send an Away Team?", people_in_hand(ctx),
                                          optional=True, none_label="No") if actions.away_targets() else None
    if person:
        yield from actions.put_on_deck(person)
        sent = (yield from actions.send_away_team(1)) is not None
    people = [i for i in ctx.me.hand + ctx.me.discard if is_suit(i, "Person") and i.uid != this.uid]
    person = yield from actions.pick_card("Log a Person from your hand or Discard pile?", people, optional=True,
                                          none_label="No")
    if person:
        yield from actions.log(person)
        logged = True
    if sent and logged:
        yield from actions.gain_resource("glory", 1)
        if (yield from actions.may("Promote Joret Dal to Duty Officer?")):
            yield from actions.promote(this)


@hand_size_modifier("1PER09")
def larger_hand(state, owner, size):
    """PASSIVE: Increase your hand size by 1."""
    return size + 1
