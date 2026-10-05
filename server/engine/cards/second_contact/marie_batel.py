"""3PIK10 Marie Batel (Person, Development). Spec: resources/scans/second_contact/cards/captains/pike/3PIK10.md"""

from engine import cards as registry
from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import has_trait, is_suit, status_of

development_cost("3PIK10", Spend(dilithium=3))
registry.DUTY_LIMIT["3PIK10"] = 1  # PASSIVE: You may have an additional Person on duty.


@operation("3PIK10", 0, uses=[A.FREE_PLAY])
def jag_officer(ctx, actions):
    """PLAY: Free play a Starfleet."""
    cards = actions.free_play_candidates(lambda i: has_trait(i, "Starfleet"))
    card = yield from actions.pick_card("Free play which Starfleet card?", cards)
    if card:
        yield from actions.free_play(card)


@operation("3PIK10", 1, uses=[A.PROMOTE])
def take_command(ctx, actions):
    """PLAY: Promote Marie Batel and a Person from your hand, Staging Area, or your Discard pile to Duty Officers."""
    if ctx.this_card in ctx.me.staging:
        yield from actions.promote(ctx.this_card)
    people = [i for i in ctx.me.hand + ctx.me.staging + ctx.me.discard if is_suit(i, "Person")]
    person = yield from actions.pick_card("Promote which other Person?", people)
    if person:
        yield from actions.promote(person)


@operation("3PIK10", 2, uses=[A.REFRESH], requires=lambda ctx: status_of(ctx.me, "3PIK02") is not None)
def support(ctx, actions):
    """ACTIVATION: Refresh Improbable, Unstoppable, Sensational."""
    yield from actions.refresh(status_of(ctx.me, "3PIK02"))
