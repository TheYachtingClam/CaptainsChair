"""1CAR16 Unstable Wormhole (Cargo). Spec: resources/scans/base_game/cards/cargo/1CAR16.md"""

from engine.cards import operation
from engine.ops import A, Spend


@operation("1CAR16", 0, uses=[A.PEEK, A.REORDER, A.DRAW])
def glimpse(ctx, actions):
    """PLAY: Look at the top 2 Location or the top 2 Encounter, and put them on the top and/or bottom of their deck in
    any order. Draw a card."""
    deck = yield from actions.choose("Look at the top 2 cards of which deck?",
                                     [("location", "The Location deck"), ("encounter", "The Encounter deck")])
    yield from actions.peek_and_reorder(2, deck=deck)
    yield from actions.draw(1)


@operation("1CAR16", 1, uses=[A.TAKE_CONTROL, A.JUNK, A.DESTROY], cost=[Spend(dilithium=3)],
           requires=lambda ctx: ctx.track("influence") >= 6 and bool(ctx.state.location_deck))
def passage(ctx, actions):
    """PLAY: Requires [Influence] 6. Spend 3 [Dilithium] to draw the top Location and take control of it. Junk a card
    from the Market. Destroy this card."""
    yield from actions.take_control(ctx.state.location_deck[0])
    yield from actions.junk()
    yield from actions.destroy(ctx.this_card)
