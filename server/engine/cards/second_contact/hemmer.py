"""3PIK20 Hemmer (Person). Spec: resources/scans/second_contact/cards/captains/pike/3PIK20.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import has_trait, is_suit, ships


def _secured(ctx):
    return [loc for loc in ctx.state.neutral if ctx.secured_by(loc)]


@operation("3PIK20", 0, uses=[A.GAIN_CARD, A.TAKE_INCIDENT], cost=[Spend(dilithium=3)])
def chief_engineer(ctx, actions):
    """PLAY: Spend 3 [Dilithium] to gain a Ship from the top of the deck, if it is Attack, take an Incident."""
    ship = yield from actions.gain_card(["Ship"], label="the top Ship", deck_only=True)
    if ship and has_trait(ship, "Attack"):
        yield from actions.take_incident()


@operation("3PIK20", 1, uses=[A.GAIN_RESOURCE, A.RECALL])
def maintenance(ctx, actions):
    """RESUPPLY: Gain 1 [Dilithium]. You may recall a card beamed to a Ship."""
    yield from actions.gain_resource("dilithium", 1)
    beamed = [b for s in ships(ctx) for b in s.beamed]
    card = yield from actions.pick_card("Recall a card beamed to a Ship?", beamed, optional=True, none_label="No")
    if card:
        yield from actions.recall(card)


@operation("3PIK20", 2, uses=[A.FREE_PLAY, A.LOG, A.TAKE_CONTROL], requires=lambda ctx: bool(_secured(ctx)))
def sacrifice(ctx, actions):
    """ACTIVATION: You may free play an Incident. Log this card to select a secured neutral Location and take control
    of it."""
    cards = actions.free_play_candidates(lambda i: is_suit(i, "Incident"))
    card = yield from actions.pick_card("Free play an Incident?", cards, optional=True, none_label="No")
    if card:
        yield from actions.free_play(card)
    targets = _secured(ctx)
    if not targets or ctx.this_card not in ctx.me.duty + ctx.me.staging:
        return
    loc = yield from actions.pick_card("Take control of which secured Location?", targets)
    yield from actions.log(ctx.this_card)
    yield from actions.take_control(loc)
