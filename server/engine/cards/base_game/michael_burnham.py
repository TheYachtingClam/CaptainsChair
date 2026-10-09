"""1BUR01 Michael Burnham (Captain). Spec: resources/scans/base_game/cards/captains/burnham/1BUR01.md"""

from engine import cards as registry
from engine.cards import operation
from engine.ops import A, Spend

# The engine runs operation 0 in her Clean-up step in place of "place 1 Glory on a Market card" (REQ-CORE-33).
registry.REPLACES_CLEANUP_GLORY["1BUR01"] = 0


@operation("1BUR01", 0, uses=[A.REMOVE_STARDATE_GLORY, A.PLACE_RESOURCES])
def seed_the_market(ctx, actions):
    """PASSIVE: During your Clean-up step, remove 1 [Glory] from the Stardate card and place 2 [Dilithium] on a card
    in the Market instead. In Cadet Training it is 1 [Dilithium] (REQ-CTM-21)."""
    amount = 1 if ctx.virtual_opponent else 2
    market = [i for i in ctx.state.market.values() if i is not None]
    target = yield from actions.pick_card(f"Place {amount} Dilithium on which Market card?", market)
    yield from actions.remove_stardate_glory(1)
    if target:
        yield from actions.place_resources(target, "dilithium", amount)


@operation("1BUR01", 1, uses=[A.GAIN_CARD, A.GAIN_RESOURCE], cost=[Spend(dilithium=3)])
def alliance(ctx, actions):
    """ACTIVATION: Spend 3 [Dilithium] to gain an Ally and 1 [Glory]."""
    yield from actions.gain_card(["Ally"], label="an Ally")
    yield from actions.gain_resource("glory", 1)
