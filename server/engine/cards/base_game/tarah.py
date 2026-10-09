"""1SHR21 Tarah (Person). Spec: resources/scans/base_game/cards/captains/shran/1SHR21.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import discard_their_top_card, has_trait, ships


@operation("1SHR21", 0, uses=[A.SEND_AWAY_TEAM])
def advance_guard(ctx, actions):
    """PLAY: Send an [Away Team] to a Location."""
    yield from actions.send_away_team(1)


operation("1SHR21", 1, uses=[A.GAIN_RESOURCE, A.ATTACK, A.DISCARD, A.TAKE_INCIDENT])(discard_their_top_card)


@operation("1SHR21", 2, uses=[A.DISCARD, A.REFRESH, A.GAIN_RESOURCE], cost=[DiscardFromHand(1)],
           requires=lambda ctx: ctx.track("military") >= 5)
def drill(ctx, actions):
    """ACTIVATION: Requires [Military] 5. Discard a card to refresh a Ship and a Location. If the discarded card is
    Weapon, gain 2 [Glory]."""
    ship = yield from actions.pick_card("Refresh which Ship?", [s for s in ships(ctx) if s.exhausted])
    if ship:
        yield from actions.refresh(ship)
    loc = yield from actions.pick_card("Refresh which Location?", [i for i in ctx.controlled_locations() if i.exhausted])
    if loc:
        yield from actions.refresh(loc)
    if actions.paid and has_trait(actions.paid[0], "Weapon"):
        yield from actions.gain_resource("glory", 2)
