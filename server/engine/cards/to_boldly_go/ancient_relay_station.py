"""2LOC01 Ancient Relay Station (Location). Spec: resources/scans/to_boldly_go/cards/location/2LOC01.md"""

from engine.cards import operation
from engine.ops import A

from ._util import others_in_hand


@operation("2LOC01", 0, uses=[A.PUT, A.SPEND, A.ENLIST_DEVELOPMENT])
def relay(ctx, actions):
    """CONTROL: You may put a card on the top of your deck and spend an [Action] to enlist a Development."""
    if others_in_hand(ctx) and actions.can_spend(actions=1) and (
            yield from actions.may("Put a card on top of your deck and spend an Action to enlist a Development?")):
        card = yield from actions.pick_card("Put which card on top of your deck?", others_in_hand(ctx))
        yield from actions.put_on_deck(card)
        yield from actions.spend(actions=1)
        yield from actions.enlist_development()
