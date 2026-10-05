"""2SHI01 Borg Probe (Ship). Spec: resources/scans/to_boldly_go/cards/ships/2SHI01.md"""

from engine.cards import operation
from engine.ops import A

from ._util import deploy_and_warp_this, warp_this_ship


@operation("2SHI01", 0, uses=[A.DEPLOY, A.WARP, A.SPEND, A.GAIN_CARD, A.LOG])
def deploy_warp_recruit(ctx, actions):
    """PLAY: Deploy and warp this ship. You may spend an [Action] and 1 [Dilithium] to gain a Person and log the
    gained card. If your Captain is Borg, assimilate it instead (no Borg Captain exists yet, so it is logged)."""
    yield from deploy_and_warp_this(ctx, actions)
    if actions.can_spend(dilithium=1, actions=1) and (
            yield from actions.may("Spend an Action and 1 Dilithium to gain a Person and log it?")):
        yield from actions.spend(dilithium=1, actions=1)
        person = yield from actions.gain_card(["Person"], label="a Person")
        if person:
            yield from actions.log(person)


operation("2SHI01", 1, uses=[A.WARP])(warp_this_ship)


@operation("2SHI01", 2, uses=[A.BEAM],
           requires=lambda ctx: any(i is not ctx.this_card for i in ctx.me.hand + ctx.me.discard))
def beam_from_hand_or_discard(ctx, actions):
    """ACTIVATION: Beam a card here from your hand or Discard pile."""
    cards = [i for i in ctx.me.hand + ctx.me.discard if i is not ctx.this_card]
    card = yield from actions.pick_card("Beam which card here (from hand or Discard pile)?", cards)
    yield from actions.beam(card, ctx.this_card)


