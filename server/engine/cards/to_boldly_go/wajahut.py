"""2KHA17 Wajahut (Person). Spec: resources/scans/to_boldly_go/cards/captains/kahn/2KHA17.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import count_traits, draw_up_to_twice, in_play_ids


@operation("2KHA17", 0, uses=[A.DISCARD, A.DRAW_FROM_DISCARD], cost=[DiscardFromHand(1)])
def scrounge(ctx, actions):
    """PLAY: Discard a card to draw a card from your Discard pile."""
    yield from actions.draw_from_discard()


@operation("2KHA17", 1, uses=[A.SEND_AWAY_TEAM, A.GAIN_ACTION, A.DRAW, A.DRAW_FROM_DISCARD])
def foray(ctx, actions):
    """PLAY: Send an [Away Team] to a neutral Location. If you have Ceti Alpha VI and Joachim in play, gain an
    [Action]. If you have a Communication in play, up to twice draw a card from your deck or Discard pile."""
    yield from actions.send_away_team(1, where=lambda loc: loc in ctx.state.neutral)
    if {"2KHA03", "2KHA18"} <= in_play_ids(ctx):
        yield from actions.gain_action(1)
    if count_traits(ctx, "Communication"):
        yield from draw_up_to_twice(ctx, actions)


@operation("2KHA17", 2, uses=[A.DISCARD, A.GAIN_ACTION, A.SPEND, A.ENLIST_DEVELOPMENT, A.DISMISS],
           cost=[DiscardFromHand(1)],
           trigger=lambda ctx, ev: ev["kind"] == "take_control" and ev["seat"] == ctx.me.seat)
def claim(ctx, actions):
    """REACTION: After you take control of a Location, discard a card to either: gain an [Action] OR spend an [Action]
    to enlist a Development and dismiss this card."""
    options = [("gain", "Gain an Action")]
    if actions.can_spend(actions=1) and ctx.me.development:
        options.append(("enlist", "Spend an Action to enlist a Development and dismiss Wajahut"))
    choice = yield from actions.choose("Wajahut: which effect?", options)
    if choice == "gain":
        yield from actions.gain_action(1)
        return
    yield from actions.spend(actions=1)
    yield from actions.enlist_development()
    yield from actions.dismiss(ctx.this_card)
