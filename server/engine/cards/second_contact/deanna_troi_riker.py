"""3RIK15 Deanna Troi-Riker (Person). Spec: resources/scans/second_contact/cards/captains/william riker/3RIK15.md"""

from engine.cards import granted_play, operation
from engine.ops import A, DiscardFromHand

from ._util import is_suit

COUNSEL = 100  # index of the PLAY that Deanna grants to Incidents


@operation("3RIK15", 0, uses=[A.PEEK, A.DISCARD, A.LOG])
def empathy(ctx, actions):
    """PLAY: Look at the top card of your deck. You may return it to the top OR discard it OR log it."""
    top = yield from actions.peek_deck()
    if top is None:
        return
    choice = yield from actions.choose(f"{ctx.name(top)}: what now?", [("keep", "Leave it on top"),
                                                                       ("discard", "Discard it"), ("log", "Log it")],
                                       show=[top])
    if choice == "discard":
        yield from actions.discard_from_deck(top)
    elif choice == "log":
        yield from actions.log(top)


@granted_play("3RIK15", COUNSEL, applies=lambda inst: is_suit(inst, "Incident"), action_cost=True,
              text="Discard a card to return this card. If you do, you may draw a card. (Deanna Troi-Riker)",
              uses=[A.DISCARD, A.RETURN_INCIDENT, A.DRAW], cost=[DiscardFromHand(1)])
def counsel(ctx, actions):
    """PASSIVE: You may treat any Incident's play operation as "[Action] PLAY: Discard a card to return this card. If
    you do, you may draw a card"."""
    yield from actions.return_incident(ctx.this_card)
    if (yield from actions.may("Draw a card?")):
        yield from actions.draw(1)


@operation("3RIK15", 2, uses=[A.REFRESH], requires=lambda ctx: ctx.me.captain.exhausted)
def support(ctx, actions):
    """ACTIVATION: Refresh your Captain."""
    yield from actions.refresh(ctx.me.captain)
