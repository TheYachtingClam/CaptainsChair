"""3RIK24 Red Alert (Incident). Spec: resources/scans/second_contact/cards/captains/william riker/3RIK24.md"""

from engine.cards import operation
from engine.ops import A, PutOnDeck

from ._util import is_suit


@operation("3RIK24", 0, uses=[A.PUT, A.RETURN_INCIDENT, A.PROMOTE], cost=[PutOnDeck()])
def battle_stations(ctx, actions):
    """PLAY: Put a card on the top of your deck to return this card. You may promote a Person from your Staging Area
    to Duty Officer."""
    yield from actions.return_incident(ctx.this_card)
    people = [i for i in ctx.me.staging if is_suit(i, "Person")]
    person = yield from actions.pick_card("Promote a Person from your Staging Area?", people, optional=True,
                                          none_label="No")
    if person:
        yield from actions.promote(person)
