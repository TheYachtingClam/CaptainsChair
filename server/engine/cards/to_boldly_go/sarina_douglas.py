"""2PER18 Sarina Douglas (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER18.md
The PLAY (which can PEEK) arrives in Step 6."""

from engine.cards import operation
from engine.ops import A

from ._util import is_suit


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
