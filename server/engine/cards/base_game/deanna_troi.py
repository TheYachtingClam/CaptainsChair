"""1PIC08 Deanna Troi (Person, Development). Spec: resources/scans/base_game/cards/captains/picard/1PIC08.md"""

from engine.cards import development_cost, granted_play, operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import draw_then_decide, is_suit

development_cost("1PIC08", Spend(dilithium=2))
COUNSEL = 101  # index of the PLAY that Troi grants to Incidents (100 is Deanna Troi-Riker's)


operation("1PIC08", 0, uses=[A.DRAW, A.DISCARD, A.GAIN_RESOURCE, A.LOG])(draw_then_decide)


@granted_play("1PIC08", COUNSEL, applies=lambda inst: is_suit(inst, "Incident"),
              text="Discard a card to return this card. If you do, draw 2 cards. (Deanna Troi)",
              uses=[A.DISCARD, A.RETURN_INCIDENT, A.DRAW], cost=[DiscardFromHand(1)])
def counsel(ctx, actions):
    """PASSIVE: You may treat any Incident's play operation as "PLAY: Discard a card to return this card. If you do,
    draw 2 cards"."""
    yield from actions.return_incident(ctx.this_card)
    yield from actions.draw(2)
