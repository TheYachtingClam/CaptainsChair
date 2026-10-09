"""1SIS21 The Wormhole (Location). Spec: resources/scans/base_game/cards/captains/sisko/1SIS21.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import has_trait, is_suit, ships


@operation("1SIS21", 0, uses=[A.TAKE_CONTROL, A.FREE_PLAY])
def discover(ctx, actions):
    """PLAY: Take control of this location. You may free play a Ship."""
    yield from actions.take_control(ctx.this_card)
    ship = yield from actions.pick_card("Free play a Ship?", actions.free_play_candidates(lambda i: is_suit(i, "Ship")),
                                        optional=True, none_label="No")
    if ship:
        yield from actions.free_play(ship)


@operation("1SIS21", 1, uses=[A.PEEK, A.REORDER])
def celestial_temple(ctx, actions):
    """CONTROL: Look at the top 3 Location and put them on the top and/or the bottom of their deck in any order."""
    yield from actions.peek_and_reorder(3, deck="location")


@operation("1SIS21", 2, uses=[A.DISCARD, A.WARP],
           cost=[DiscardFromHand(1, lambda ctx, i: is_suit(i, "Person"), "a Person")],
           requires=lambda ctx: bool(ships(ctx)))
def transit(ctx, actions):
    """ACTIVATION: Discard a Person to warp a Ship."""
    ship = yield from actions.pick_card("Warp which Ship?", [s for s in ships(ctx) if actions.can_warp(s)])
    if ship:
        yield from actions.warp(ship)


@operation("1SIS21", 3, uses=[A.DISCARD, A.FIND], cost=[DiscardFromHand(1)])
def survey(ctx, actions):
    """ACTIVATION: Discard a card to find an Anomaly."""
    yield from actions.find(lambda i: has_trait(i, "Anomaly"), "an Anomaly")
