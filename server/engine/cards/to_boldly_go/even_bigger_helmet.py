"""2REB12 Even Bigger Helmet (Cargo). Spec: resources/scans/to_boldly_go/cards/captains/rebner/2REB12.md"""

from engine.cards import operation
from engine.ops import A, TakeIncidentCost

from ._util import is_suit


@operation("2REB12", 0, uses=[A.GAIN_RESOURCE, A.PROMOTE])
def status_symbol(ctx, actions):
    """PLAY: Gain 1 [Latinum] and 1 [Dilithium]. Promote a Person from your hand or Staging Area to Duty Officer."""
    yield from actions.gain_resource("latinum", 1)
    yield from actions.gain_resource("dilithium", 1)
    person = yield from actions.pick_card("Promote which Person?",
                                          [i for i in ctx.me.hand + ctx.me.staging if is_suit(i, "Person")])
    if person:
        yield from actions.promote(person)


@operation("2REB12", 1, uses=[A.TAKE_INCIDENT, A.ENLIST_DEVELOPMENT], cost=[TakeIncidentCost()],
           requires=lambda ctx: any(i.card == "2REB03" for i in ctx.me.development))
def bigger_still(ctx, actions):
    """PLAY: Take an Incident to enlist Big Enough Helmet."""
    yield from actions.enlist_development(pred=lambda i: i.card == "2REB03")
