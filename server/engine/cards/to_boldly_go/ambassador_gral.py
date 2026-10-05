"""2PER02 Ambassador Gral (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER02.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_suit


@operation("2PER02", 0, uses=[A.FIND])
def negotiate(ctx, actions):
    """PLAY: Find a card with [Influence]/[Influence Focus]."""
    yield from actions.find(lambda i: ctx.has_specialty_icon(i, "influence"), "a card with Influence")


@operation("2PER02", 1, uses=[A.ATTACK, A.DISMISS, A.GAIN_RESOURCE, A.PROMOTE])
def provoke(ctx, actions):
    """ATTACK PLAY: Dismiss an opponent Vulcan/Andorian (of your choice) to gain 1 [Glory]. You may promote a Person
    with Tellarite from your hand or Staging Area to Duty Officer (can be this card)."""
    if (yield from actions.attack()):
        opp = ctx.opponent
        if opp is None:
            yield from actions.gain_resource("glory", 1)  # the virtual opponent has one of everything
        else:
            targets = [i for i in [*opp.fleet, *opp.duty, *opp.status] if has_trait(i, "Vulcan", "Andorian")]
            target = yield from actions.pick_card("Dismiss which opponent Vulcan or Andorian?", targets)
            if target:
                yield from actions.dismiss(target)
                yield from actions.gain_resource("glory", 1)
    tellarites = [i for i in ctx.me.hand + ctx.me.staging if is_suit(i, "Person") and has_trait(i, "Tellarite")]
    person = yield from actions.pick_card("Promote a Tellarite from your hand or Staging Area?", tellarites,
                                          optional=True, none_label="No")
    if person:
        yield from actions.promote(person)


@operation("2PER02", 2, uses=[A.ATTACK, A.GIVE],
           trigger=lambda ctx, ev: ev["kind"] == "would_return_incident" and ev["seat"] == ctx.me.seat)
def protest(ctx, actions):
    """ATTACK REACTION: When you would return an Incident, give it to your opponent instead.
    Ruling: if the opponent ignores the attack, the Incident is returned as normal."""
    incident = ctx.event_card
    if incident is None or not (yield from actions.attack()):
        return False
    yield from actions.give_incident(incident)
    return True
