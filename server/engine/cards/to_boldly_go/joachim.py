"""2KHA18 Joachim (Person). Spec: resources/scans/to_boldly_go/cards/captains/kahn/2KHA18.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, TakeIncidentCost

from ._util import count_traits, draw_up_to_twice, in_play_ids, is_suit


@operation("2KHA18", 0, uses=[A.TAKE_INCIDENT, A.GAIN_CARD], cost=[TakeIncidentCost()])
def conscript(ctx, actions):
    """PLAY: Take an Incident to gain a Person from the top of the deck."""
    yield from actions.gain_card(["Person"], label="the top Person", deck_only=True)


@operation("2KHA18", 1, uses=[A.SEND_AWAY_TEAM, A.GAIN_ACTION, A.DRAW, A.DRAW_FROM_DISCARD])
def raid(ctx, actions):
    """PLAY: Send an [Away Team] to a neutral Location. If you have Ceti Alpha VI and Wajahut in play, gain an
    [Action]. If you have a Weapon or Security in play, up to twice draw a card from your deck or Discard pile."""
    yield from actions.send_away_team(1, where=lambda loc: loc in ctx.state.neutral)
    if {"2KHA03", "2KHA17"} <= in_play_ids(ctx):
        yield from actions.gain_action(1)
    if count_traits(ctx, "Weapon", "Security"):
        yield from draw_up_to_twice(ctx, actions)


@operation("2KHA18", 2, uses=[A.DISCARD, A.SEND_AWAY_TEAM], cost=[DiscardFromHand(1)],
           trigger=lambda ctx, ev: ev["kind"] == "deploy" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and is_suit(ctx.event_card, "Ship"))
def first_officer(ctx, actions):
    """REACTION: After deploying a Ship, discard a card to send an [Away Team] to a neutral Location."""
    yield from actions.send_away_team(1, where=lambda loc: loc in ctx.state.neutral)
