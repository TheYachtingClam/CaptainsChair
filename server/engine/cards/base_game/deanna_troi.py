"""1PIC08 Deanna Troi (Person, Development). Spec: resources/scans/base_game/cards/captains/picard/1PIC08.md"""

from engine.cards import development_cost, granted_play, operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import is_suit

development_cost("1PIC08", Spend(dilithium=2))
COUNSEL = 101  # index of the PLAY that Troi grants to Incidents (100 is Deanna Troi-Riker's)


def draw_then_decide(ctx, actions):
    """Draw a card, then either: keep it OR discard it to gain 1 [Glory] OR log it."""
    before = [i.uid for i in ctx.me.hand]
    yield from actions.draw(1)
    drawn = next((i for i in ctx.me.hand if i.uid not in before), None)
    if drawn is None:
        return
    choice = yield from actions.choose(f"{ctx.name(drawn)}: what now?",
                                       [("keep", "Keep it"), ("discard", "Discard it to gain 1 Glory"), ("log", "Log it")],
                                       show=[drawn])
    if choice == "discard":
        yield from actions.discard(1, pred=lambda i: i.uid == drawn.uid)
        yield from actions.gain_resource("glory", 1)
    elif choice == "log":
        yield from actions.log(drawn)


operation("1PIC08", 0, uses=[A.DRAW, A.DISCARD, A.GAIN_RESOURCE, A.LOG])(draw_then_decide)


@granted_play("1PIC08", COUNSEL, applies=lambda inst: is_suit(inst, "Incident"),
              text="Discard a card to return this card. If you do, draw 2 cards. (Deanna Troi)",
              uses=[A.DISCARD, A.RETURN_INCIDENT, A.DRAW], cost=[DiscardFromHand(1)])
def counsel(ctx, actions):
    """PASSIVE: You may treat any Incident's play operation as "PLAY: Discard a card to return this card. If you do,
    draw 2 cards"."""
    yield from actions.return_incident(ctx.this_card)
    yield from actions.draw(2)
