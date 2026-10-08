"""2KHA16 S.S. Botany Bay (Ship). Spec: resources/scans/to_boldly_go/cards/captains/kahn/2KHA16.md"""

from engine.cards import CANNOT_WARP, operation
from engine.ops import A, TakeIncidentCost

from ._util import is_suit, others_in_hand

CANNOT_WARP.add("2KHA16")  # PASSIVE: This ship cannot be warped.


def _people_in_hand(ctx):
    return others_in_hand(ctx, lambda i: is_suit(i, "Person"))


def _people_here(ctx):
    return [b for b in ctx.this_card.beamed if is_suit(b, "Person")]


@operation("2KHA16", 0, uses=[A.TAKE_INCIDENT, A.DEPLOY, A.PROMOTE, A.BEAM], cost=[TakeIncidentCost()])
def thaw(ctx, actions):
    """PLAY: Take an Incident to deploy this ship. You may promote a Person from your hand or Discard pile to Duty
    Officer. You may beam a Person here."""
    ship = ctx.this_card
    yield from actions.deploy(ship)
    people = _people_in_hand(ctx) + [i for i in ctx.me.discard if is_suit(i, "Person")]
    person = yield from actions.pick_card("Promote a Person from your hand or Discard pile?", people, optional=True,
                                          none_label="No")
    if person is not None:
        yield from actions.promote(person)
    sleeper = yield from actions.pick_card("Beam a Person here?", _people_in_hand(ctx), optional=True, none_label="No")
    if sleeper is not None:
        yield from actions.beam(sleeper, ship)


@operation("2KHA16", 2, uses=[A.BEAM], requires=lambda ctx: bool(_people_in_hand(ctx)))
def cryo_tube(ctx, actions):
    """ACTIVATION: Beam a Person here."""
    person = yield from actions.pick_card("Beam which Person here?", _people_in_hand(ctx))
    yield from actions.beam(person, ctx.this_card)


@operation("2KHA16", 3, uses=[A.DISMISS, A.PEEK, A.TAKE_CONTROL, A.PUT, A.LOG],
           requires=lambda ctx: len(_people_here(ctx)) >= 3)
def colonise(ctx, actions):
    """ACTIVATION: If there are 3+ Person beamed here, dismiss all of them to look at the top 2 Location, take control
    of one of them and return the other to the bottom of its deck. Log this card."""
    for person in _people_here(ctx):
        yield from actions.dismiss(person)
    top = yield from actions.peek_location_deck(2)
    if top:
        chosen = yield from actions.pick_card("Take control of which Location?", top)
        for other in top:
            if other.uid != chosen.uid:
                yield from actions.put_on_location_deck(other, bottom=True)
        yield from actions.take_control(chosen)
    yield from actions.log(ctx.this_card)
