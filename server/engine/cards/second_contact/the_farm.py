"""3FRE08 The Farm (Location, Development). Spec: resources/scans/second_contact/cards/captains/freeman/3FRE08.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import has_trait, is_suit, others_in_hand

development_cost("3FRE08", Spend(latinum=2, dilithium=2))


@operation("3FRE08", 0, uses=[A.TAKE_CONTROL])
def take_control(ctx, actions):
    """PLAY: Take control of this location."""
    yield from actions.take_control(ctx.this_card)


@operation("3FRE08", 1, uses=[A.FREE_PLAY])
def triage(ctx, actions):
    """CONTROL: You may free play an Incident."""
    cards = actions.free_play_candidates(lambda i: is_suit(i, "Incident"))
    card = yield from actions.pick_card("Free play an Incident?", cards, optional=True, none_label="No")
    if card:
        yield from actions.free_play(card)


@operation("3FRE08", 2, uses=[A.BEAM], requires=lambda ctx: bool(others_in_hand(ctx)))
def admit(ctx, actions):
    """ACTIVATION: Beam a card here."""
    card = yield from actions.pick_card("Beam which card to The Farm?", others_in_hand(ctx))
    yield from actions.beam(card, ctx.this_card)


@operation("3FRE08", 3, uses=[A.LOG, A.TAKE_ENCOUNTER], requires=lambda ctx: ctx.track("research") >= 5)
def study(ctx, actions):
    """ACTIVATION: Requires [Research] 5. Log all cards beamed here. If at least 2 of the logged cards have Anomaly,
    take the top Encounter and log this card."""
    anomalies = 0
    for card in list(ctx.this_card.beamed):
        anomalies += has_trait(card, "Anomaly")
        yield from actions.log(card)
    if anomalies >= 2:
        yield from actions.take_encounter()
        yield from actions.log(ctx.this_card)
