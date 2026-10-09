"""0CAR01 Sehlat (Cargo, promo). Spec: resources/scans/promo1/cards/cargo/0CAR01.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_suit


def _vulcan_person(i):
    return is_suit(i, "Person") and has_trait(i, "Vulcan")


@operation("0CAR01", 0, uses=[A.FIND, A.ATTACK, A.FORCE, A.DISCARD])
def pet(ctx, actions):
    """ATTACK PLAY: Find a Vulcan. Force your opponent to discard a Person."""
    yield from actions.find(lambda i: has_trait(i, "Vulcan"), "a Vulcan")
    if (yield from actions.attack()) and ctx.opponent is not None:
        yield from actions.discard(1, pred=lambda i: is_suit(i, "Person"), label="a Person", player=ctx.opponent)


@operation("0CAR01", 1, uses=[A.FREE_PLAY],
           requires=lambda ctx: any(_vulcan_person(i) and i is not ctx.this_card for i in ctx.me.hand))
def companion(ctx, actions):
    """PLAY: Free play a Person with Vulcan."""
    this = ctx.this_card
    people = [i for i in actions.free_play_candidates(_vulcan_person) if i.uid != this.uid]
    person = yield from actions.pick_card("Free play which Vulcan Person?", people)
    if person:
        yield from actions.free_play(person)


@operation("0CAR01", 2, uses=[A.PROMOTE],
           requires=lambda ctx: any(_vulcan_person(i) for i in ctx.me.hand + ctx.me.staging))
def guardian(ctx, actions):
    """PLAY: Promote a Person with Vulcan from your hand or Staging Area to Duty Officer."""
    people = [i for i in ctx.me.hand + ctx.me.staging if _vulcan_person(i)]
    person = yield from actions.pick_card("Promote which Vulcan Person?", people)
    if person:
        yield from actions.promote(person)
