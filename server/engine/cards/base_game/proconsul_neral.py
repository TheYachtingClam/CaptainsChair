"""1SEL05 Proconsul Neral (Person, Development). Spec: resources/scans/base_game/cards/captains/sela/1SEL05.md"""

from engine.cards import development_cost, operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import has_trait, is_suit, others_in_hand

development_cost("1SEL05", Spend(dilithium=2))


def _romulan(i):
    return has_trait(i, "Romulan")


@operation("1SEL05", 0, uses=[A.FIND, A.FREE_PLAY, A.DISCARD, A.PROMOTE])
def decree(ctx, actions):
    """PLAY: Find any card. You may free play an Incident. You may discard a Romulan to promote this card to Duty
    Officer."""
    yield from actions.find(lambda i: True, "any card")
    incidents = actions.free_play_candidates(lambda i: is_suit(i, "Incident"))
    incident = yield from actions.pick_card("Free play an Incident?", incidents, optional=True, none_label="No")
    if incident:
        yield from actions.free_play(incident)
    if others_in_hand(ctx, _romulan) and (yield from actions.may("Discard a Romulan to promote Proconsul Neral?")):
        yield from actions.discard(1, pred=_romulan, label="a Romulan")
        yield from actions.promote(ctx.this_card)


@operation("1SEL05", 1, uses=[A.DISCARD, A.GAIN_ACTION], cost=[DiscardFromHand(1)],
           trigger=lambda ctx, ev: ev["kind"] == "take_control" and ev["seat"] == ctx.me.seat)
def annexation(ctx, actions):
    """REACTION: After you take control of a Location, discard a card to gain an [Action]."""
    yield from actions.gain_action(1)
