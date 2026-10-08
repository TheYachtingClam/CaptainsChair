"""2KHA04 Hijacked U.S.S. Reliant (Ship, Development). Spec: resources/scans/to_boldly_go/cards/captains/kahn/2KHA04.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Condition, DiscardFromHand, Spend

from ._util import beam_a_card_here, can_discard_then_beam, is_suit, opponent_ships, others_in_hand

development_cost("2KHA04", Spend(dilithium=3),
                 Condition(lambda ctx: ctx.count_in_play(lambda i: is_suit(i, "Person") and ctx.has(i, "Mind Control")) > 0,
                           "have a Person with Mind Control in play"))


@operation("2KHA04", 0, uses=[A.DEPLOY, A.SEND_AWAY_TEAM, A.DRAW])
def hijack(ctx, actions):
    """PLAY: Deploy this ship. If your opponent has at most 1 Ship deployed: send an [Away Team] to a Location and
    draw a card. Cadet Training: the virtual opponent has one Ship."""
    yield from actions.deploy(ctx.this_card)
    if len(opponent_ships(ctx)) <= 1:
        yield from actions.send_away_team(1)
        yield from actions.draw(1)


@operation("2KHA04", 1, uses=[A.WARP], cost=[Spend(dilithium=1)])
def warp(ctx, actions):
    """ACTIVATION: Spend 1 [Dilithium] to warp this ship."""
    yield from actions.warp(ctx.this_card)


@operation("2KHA04", 2, uses=[A.DISCARD, A.BEAM], cost=[DiscardFromHand(1)], requires=can_discard_then_beam)
def beam(ctx, actions):
    """ACTIVATION: Discard a card to beam a card here."""
    yield from beam_a_card_here(ctx, actions)


@operation("2KHA04", 3, uses=[A.PROMOTE], requires=lambda ctx: bool(others_in_hand(ctx, lambda i: is_suit(i, "Person"))))
def promote(ctx, actions):
    """ACTIVATION: Promote a Person from your hand to Duty Officer."""
    person = yield from actions.pick_card("Promote which Person?", others_in_hand(ctx, lambda i: is_suit(i, "Person")))
    yield from actions.promote(person)


