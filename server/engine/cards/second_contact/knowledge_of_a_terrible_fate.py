"""3PIK17 Knowledge of a Terrible Fate (Directive, Ongoing). Spec: resources/scans/second_contact/cards/captains/pike/3PIK17.md"""

from engine.cards import operation
from engine.ops import A, LogFromHand

from ._util import is_suit


@operation("3PIK17", 0, uses=[A.DEPLOY])
def deploy(ctx, actions):
    """PLAY: Deploy this card."""
    yield from actions.deploy(ctx.this_card)


@operation("3PIK17", 1, uses=[A.JUNK])
def fate(ctx, actions):
    """RESUPPLY: Junk a Person/Ally from your Development pile."""
    card = yield from actions.pick_card("Junk which Person or Ally from your Development pile?",
                                        [i for i in ctx.me.development if is_suit(i, "Person", "Ally")])
    if card:
        yield from actions.junk_card(card)


@operation("3PIK17", 2, uses=[A.LOG, A.DESTROY], cost=[LogFromHand(lambda ctx, i: is_suit(i, "Encounter"), "an Encounter")])
def defy_fate(ctx, actions):
    """ACTIVATION: Log an Encounter (from your hand) to destroy this card."""
    yield from actions.destroy(ctx.this_card)


@operation("3PIK17", 3, uses=[A.DRAW], trigger=lambda ctx, ev: ev["kind"] == "take_incident" and ev["seat"] == ctx.me.seat)
def foresight(ctx, actions):
    """REACTION: After taking an Incident, draw 2 cards."""
    yield from actions.draw(2)


@operation("3PIK17", 4, uses=[A.GAIN_RESOURCE, A.DISCARD, A.DESTROY])
def surprise(ctx, actions):
    """SURPRISE (Bot only): Gain 1 [Glory]. Discard the bottom card of the Supplement deck. Destroy this card."""
    yield from actions.gain_resource("glory", 1)
    yield from actions.discard_from_reserve(bottom=True)
    yield from actions.destroy(ctx.this_card)
