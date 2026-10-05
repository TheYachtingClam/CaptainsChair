"""2GEO03 Kaminar (Location). Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO03.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import has_trait, is_suit

development_cost("2GEO03", Spend(dilithium=3))


@operation("2GEO03", 0, uses=[A.TAKE_CONTROL])
def take_control(ctx, actions):
    """PLAY: Take control of this location."""
    yield from actions.take_control(ctx.this_card)


@operation("2GEO03", 1, uses=[A.FIND, A.PROMOTE])
def find_kelpien(ctx, actions):
    """CONTROL: Find a Kelpien. If the found card is a Person, you may promote them to Duty Officer."""
    found, _ = yield from actions.find(lambda i: has_trait(i, "Kelpien"), "a Kelpien")
    if found and is_suit(found, "Person") and (yield from actions.may(f"Promote {ctx.name(found)} to Duty Officer?")):
        yield from actions.promote(found)


@operation("2GEO03", 2, uses=[A.SPEND, A.FREE_PLAY, A.DRAW])
def play_kelpien(ctx, actions):
    """ACTIVATION: You may spend 1 Dilithium to free play a Kelpien. If you have an Away Team here, draw a card."""
    candidates = actions.free_play_candidates(lambda i: has_trait(i, "Kelpien"))
    from engine.ops import can_afford

    if candidates and can_afford(ctx.me, dilithium=1) and (yield from actions.may("Spend 1 Dilithium to free play a Kelpien?")):
        yield from actions.spend(dilithium=1)
        card = yield from actions.pick_card("Free play which Kelpien?", candidates)
        yield from actions.free_play(card)
    if ctx.away_at(ctx.this_card) > 0:
        yield from actions.draw(1)


@operation("2GEO03", 3, uses=[A.RETURN_INCIDENT], requires=lambda ctx: bool(ctx.hand_incidents()))
def return_incident(ctx, actions):
    """ACTIVATION: Return an Incident."""
    incident = yield from actions.pick_card("Return which Incident?", ctx.hand_incidents())
    yield from actions.return_incident(incident)
