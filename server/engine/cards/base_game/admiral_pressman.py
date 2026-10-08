"""1PER03 Admiral Pressman (Person). Spec: resources/scans/base_game/cards/person/1PER03.md"""

from engine.cards import operation
from engine.ops import A, DismissFromPlay

from ._util import count_traits, has_trait, is_suit


@operation("1PER03", 0, uses=[A.FREE_PLAY, A.PROMOTE])
def covert_orders(ctx, actions):
    """PLAY: Free play an Attack. If you have no Duty Officer, you may promote a Person to Duty Officer from your hand
    or Discard pile."""
    this = ctx.this_card
    attacks = [i for i in actions.free_play_candidates(lambda i: has_trait(i, "Attack")) if i.uid != this.uid]
    attack = yield from actions.pick_card("Free play which Attack?", attacks)
    if attack:
        yield from actions.free_play(attack)
    if not ctx.me.duty:
        people = [i for i in ctx.me.hand + ctx.me.discard if is_suit(i, "Person") and i.uid != this.uid]
        person = yield from actions.pick_card("Promote a Person from your hand or Discard pile?", people, optional=True,
                                              none_label="No")
        if person:
            yield from actions.promote(person)


@operation("1PER03", 1, uses=[A.DRAW])
def security_detail(ctx, actions):
    """RESUPPLY: Draw a card for each Security you have in play (max 3)."""
    n = min(3, count_traits(ctx, "Security"))
    if n:
        yield from actions.draw(n)


@operation("1PER03", 2, uses=[A.DISMISS, A.LOG, A.GAIN_RESOURCE],
           cost=[DismissFromPlay(lambda ctx, i: has_trait(i, "Cloak"), "a Cloak")])
def pegasus(ctx, actions):
    """ACTIVATION: Dismiss a Cloak you have in play to log this card and gain 3 [Glory]."""
    yield from actions.log(ctx.this_card)
    yield from actions.gain_resource("glory", 3)
