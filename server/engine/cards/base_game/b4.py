"""1PER05 B-4 (Person). Spec: resources/scans/base_game/cards/person/1PER05.md"""

from engine.cards import operation
from engine.ops import A, TakeIncidentCost

from ._util import has_trait, others_in_hand


@operation("1PER05", 0, uses=[A.GAIN_CARD])
def salvage(ctx, actions):
    """PLAY: Gain a Cargo from the Junk."""
    yield from actions.gain_card(["Cargo"], label="a Cargo from the Junk", only_junk=True)


@operation("1PER05", 1, uses=[A.TAKE_INCIDENT, A.SCAN_FOR], cost=[TakeIncidentCost()])
def prototype(ctx, actions):
    """PLAY: Take an Incident to scan for a Synthetic, including from the Junk."""
    yield from actions.scan_for(lambda i: has_trait(i, "Synthetic"), "a Synthetic", include_junk=True)


@operation("1PER05", 2, uses=[A.LOG, A.ATTACK, A.TAKE_INCIDENT, A.GAIN_RESOURCE],
           requires=lambda ctx: bool(others_in_hand(ctx)))
def download(ctx, actions):
    """ATTACK ACTIVATION: Log a card from your hand. If you do, your opponent takes an Incident and you gain 1
    [Dilithium] for every 2 cards in your Log (rounded down)."""
    card = yield from actions.pick_card("Log which card from your hand?", others_in_hand(ctx))
    if not card:
        return
    yield from actions.log(card)
    if (yield from actions.attack()):
        yield from actions.take_incident(opponent=True)
    n = len(ctx.me.log) // 2
    if n:
        yield from actions.gain_resource("dilithium", n)
