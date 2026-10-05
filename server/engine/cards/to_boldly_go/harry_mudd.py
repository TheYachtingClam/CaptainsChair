"""2PER06 Harry Mudd (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER06.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_suit


def _recallable(ctx):
    return [i for i in ctx.me.staging if not has_trait(i, "Time Travel")]


@operation("2PER06", 1, uses=[A.DISMISS, A.RECALL], requires=lambda ctx: bool(_recallable(ctx)))
def skip_town(ctx, actions):
    """ACTIVATION: Dismiss this card to recall a non-Time Travel card from your Staging Area."""
    yield from actions.dismiss(ctx.this_card)
    card = yield from actions.pick_card("Recall which card from your Staging Area?", _recallable(ctx))
    yield from actions.recall(card)


@operation("2PER06", 0, uses=[A.ATTACK, A.FORCE, A.LOG, A.DRAW, A.TAKE_INCIDENT, A.PROMOTE],
           requires=lambda ctx: ctx.track("influence") >= 3)
def con(ctx, actions):
    """ATTACK PLAY: Requires [Influence] 3. Force your opponent to log a Person from their hand or Discard pile. If
    they do, they may draw a card. If they cannot, they take an Incident. You may promote this card to Duty Officer."""
    if (yield from actions.attack()) and ctx.opponent is not None:
        opp = ctx.opponent
        people = [i for i in opp.hand + opp.discard if is_suit(i, "Person")]
        if people:
            person = yield from actions.pick_card("Harry Mudd: log a Person from your hand or Discard pile.", people,
                                                  seat=opp.seat)
            yield from actions.log(person)
            if (yield from actions.may("Draw a card?", seat=opp.seat)):
                yield from actions.draw(1, player=opp)
        else:
            yield from actions.take_incident(opponent=True)
    if ctx.this_card in ctx.me.staging and (yield from actions.may("Promote Harry Mudd to Duty Officer?")):
        yield from actions.promote(ctx.this_card)
