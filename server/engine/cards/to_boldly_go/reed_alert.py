"""2INC04 Reed Alert (Incident). Spec: resources/scans/to_boldly_go/cards/incident/2INC04.md"""

from engine.cards import operation
from engine.ops import A, PutOnDeck

from ._util import is_suit


@operation("2INC04", 0, uses=[A.PUT, A.RETURN_INCIDENT, A.PROMOTE, A.GAIN_RESOURCE], cost=[PutOnDeck(1)])
def red_alert(ctx, actions):
    """PLAY: Put a card on the top of your deck to return this card. You may promote a Person from your Staging Area
    to Duty Officer. If you have Malcolm Reed in play, gain 1 [Glory]."""
    yield from actions.return_incident(ctx.this_card)
    people = [i for i in ctx.me.staging if is_suit(i, "Person")]
    person = yield from actions.pick_card("Promote a Person from your Staging Area?", people, optional=True,
                                          none_label="No")
    if person:
        yield from actions.promote(person)
    if ctx.count_in_play(lambda i: i.card == "2PER11"):
        yield from actions.gain_resource("glory", 1)
