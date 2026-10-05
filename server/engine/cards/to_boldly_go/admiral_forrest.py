"""2ARC08 Admiral Forrest (Person, Development). Spec: resources/scans/to_boldly_go/cards/captains/archer/2ARC08.md"""

from engine import cards as registry
from engine.cards import development_cost, operation
from engine.ops import A, Condition, DiscardFromHand

from ._util import earth_of, is_suit

development_cost("2ARC08", Condition(lambda ctx: earth_of(ctx.me) is not None and len(earth_of(ctx.me).beamed) >= 4,
                                     "4+ cards beamed to Earth"))
registry.DUTY_LIMIT["2ARC08"] = 2  # PASSIVE: You may have up to two additional Person on duty.


@operation("2ARC08", 0, uses=[A.FREE_PLAY, A.PROMOTE])
def command(ctx, actions):
    """PLAY: You may free play an Incident or a Directive. You may promote Admiral Forrest and up to 2 other Person
    from your hand, Discard pile, or Staging Area to Duty Officer(s)."""
    cards = actions.free_play_candidates(lambda i: is_suit(i, "Incident", "Directive"))
    card = yield from actions.pick_card("Free play an Incident or Directive?", cards, optional=True, none_label="No")
    if card:
        yield from actions.free_play(card)
    if ctx.this_card in ctx.me.staging and (yield from actions.may("Promote Admiral Forrest?")):
        yield from actions.promote(ctx.this_card)
        for n in (1, 2):
            people = [i for i in ctx.me.hand + ctx.me.discard + ctx.me.staging if is_suit(i, "Person")]
            person = yield from actions.pick_card(f"Promote another Person ({n} of up to 2)?", people, optional=True,
                                                  none_label="Stop")
            if not person:
                break
            yield from actions.promote(person)


@operation("2ARC08", 1, uses=[A.DISCARD, A.PLACE_RESOURCES], cost=[DiscardFromHand(1)],
           requires=lambda ctx: earth_of(ctx.me) is not None)
def appropriations(ctx, actions):
    """ACTIVATION: Discard a card to place 1 [Glory] on Earth."""
    yield from actions.place_resources(earth_of(ctx.me), "glory", 1)
