"""2ENC03 Guardian of Forever (Encounter). Spec: resources/scans/to_boldly_go/cards/encounter/2ENC03.md"""

from engine import cards as registry
from engine.cards import hand_size_modifier, operation
from engine.ops import A

from ._util import has_trait


@operation("2ENC03", 0, uses=[A.GAIN_SPECIALTY, A.DEPLOY])
def gateway(ctx, actions):
    """PLAY: Gain 1 [Influence] and 1 [Research]. Deploy this card."""
    yield from actions.gain_specialty("influence", 1)
    yield from actions.gain_specialty("research", 1)
    yield from actions.deploy(ctx.this_card)


@hand_size_modifier("2ENC03")
def larger_hand(state, owner, size):
    """PASSIVE: Increase your hand size by 1. (Its other half, scanning the Junk, is SCANS_INCLUDE_JUNK below.)"""
    return size + 1


registry.SCANS_INCLUDE_JUNK.add("2ENC03")  # PASSIVE: Whenever scanning, include cards in the Junk too.


@operation("2ENC03", 2, uses=[A.RECALL, A.TAKE_INCIDENT, A.GAIN_ACTION, A.LOG])
def time_portal(ctx, actions):
    """ACTIVATION: Recall a non-Time Travel card from your Staging Area. You may take an Incident to gain an [Action].
    Log this card."""
    cards = [i for i in ctx.me.staging if not has_trait(i, "Time Travel")]
    card = yield from actions.pick_card("Recall which card from your Staging Area?", cards)
    if card:
        yield from actions.recall(card)
    if ctx.state.incident and (yield from actions.may("Take an Incident to gain an Action?")):
        yield from actions.take_incident()
        yield from actions.gain_action(1)
    yield from actions.log(ctx.this_card)
