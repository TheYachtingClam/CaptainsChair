"""2GEO19 Vulcan Science Academy (Location). Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO19.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait


@operation("2GEO19", 0, uses=[A.TAKE_CONTROL])
def take_control(ctx, actions):
    """PLAY: Take control of this location."""
    yield from actions.take_control(ctx.this_card)


@operation("2GEO19", 1, uses=[A.GAIN_CARD, A.GAIN_RESOURCE])
def gain_person(ctx, actions):
    """CONTROL: You may gain a Person. If the gained card is Vulcan, gain 2 Dilithium. If it is Scientist,
    gain 1 Glory. If it has both traits, gain both rewards."""
    if not (yield from actions.may("Gain a Person?")):
        return
    person = yield from actions.gain_card(["Person"], label="a Person")
    if person and has_trait(person, "Vulcan"):
        yield from actions.gain_resource("dilithium", 2)
    if person and has_trait(person, "Scientist"):
        yield from actions.gain_resource("glory", 1)


@operation("2GEO19", 2, uses=[A.DRAW])
def draw(ctx, actions):
    """ACTIVATION: If you have an Away Team here, draw a card. If you have 3+ total Away Teams on 1 or more
    controlled Location, draw a card."""
    n = (1 if ctx.away_at(ctx.this_card) > 0 else 0) + (1 if sum(ctx.away_at(l) for l in ctx.me.locations) >= 3 else 0)
    if n:
        yield from actions.draw(n)
