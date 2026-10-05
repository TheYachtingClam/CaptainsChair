"""2PER18 Sarina Douglas (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER18.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import has_trait, is_suit


@operation("2PER18", 1, uses=[A.DISCARD, A.TAKE_INCIDENT, A.DISMISS])
def instability(ctx, actions):
    """RESUPPLY: Discard an Incident OR take an Incident OR dismiss this card."""
    options = ([("discard", "Discard an Incident")] if any(is_suit(i, "Incident") for i in ctx.me.hand) else []) + \
        [("take", "Take an Incident"), ("dismiss", "Dismiss Sarina Douglas")]
    choice = yield from actions.choose("Sarina Douglas: choose one.", options)
    if choice == "discard":
        yield from actions.discard(1, pred=lambda i: is_suit(i, "Incident"), label="an Incident")
    elif choice == "take":
        yield from actions.take_incident()
    else:
        yield from actions.dismiss(ctx.this_card)


@operation("2PER18", 2, uses=[A.FREE_PLAY])
def episode(ctx, actions):
    """ACTIVATION: Free play an Incident from your Discard pile."""
    cards = actions.free_play_candidates(lambda i: is_suit(i, "Incident"), zones_=("discard",))
    card = yield from actions.pick_card("Free play which Incident from your Discard pile?", cards)
    if card:
        yield from actions.free_play(card)


@operation("2PER18", 0, uses=[A.DISCARD, A.FREE_PLAY, A.PEEK],
           cost=[DiscardFromHand(1, lambda ctx, i: has_trait(i, "Doctor", "Augment"), "a Doctor or Augment")])
def augmented_insight(ctx, actions):
    """PLAY: Discard a Doctor/Augment to either: free play a card with [Research]/[Research Focus] OR look at the top
    card of a Market deck."""
    playable = actions.free_play_candidates(lambda i: ctx.has_specialty_icon(i, "research"))
    options = ([("play", "Free play a card with Research")] if playable else []) + \
        [("peek", "Look at the top card of a Market deck")]
    choice = options[0][0] if len(options) == 1 else (yield from actions.choose("Sarina Douglas: choose one.", options))
    if choice == "play":
        card = yield from actions.pick_card("Free play which card?", playable)
        yield from actions.free_play(card)
    else:
        yield from actions.peek_market_deck()
