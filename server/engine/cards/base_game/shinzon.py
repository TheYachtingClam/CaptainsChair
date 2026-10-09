"""1SEL06 Shinzon (Person, Development). Spec: resources/scans/base_game/cards/captains/sela/1SEL06.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import has_trait

development_cost("1SEL06", Spend(dilithium=3))
SCIMITAR = "1SEL07"


@operation("1SEL06", 0, uses=[A.ATTACK, A.TAKE_INCIDENT, A.SPEND, A.SCAN_FOR, A.FREE_PLAY])
def praetor(ctx, actions):
    """ATTACK PLAY: Your opponent takes an Incident. You may spend 2 [Latinum] to scan for a Synthetic. You may free
    play the Scimitar (from your hand)."""
    if (yield from actions.attack()):
        yield from actions.take_incident(opponent=True)
    if actions.can_spend(latinum=2) and (yield from actions.may("Spend 2 Latinum to scan for a Synthetic?")):
        yield from actions.spend(latinum=2)
        yield from actions.scan_for(lambda i: has_trait(i, "Synthetic"), "a Synthetic")
    scimitar = actions.free_play_candidates(lambda i: i.card == SCIMITAR)
    if scimitar and (yield from actions.may("Free play the Scimitar?")):
        yield from actions.free_play(scimitar[0])


@operation("1SEL06", 1, uses=[A.LOG, A.GAIN_SPECIALTY])
def purge(ctx, actions):
    """RESUPPLY: Log a Romulan from your hand or Discard pile, if able. If you do, gain 1 [Military]."""
    romulans = [i for i in ctx.me.hand + ctx.me.discard if has_trait(i, "Romulan")]
    romulan = yield from actions.pick_card("Shinzon: log which Romulan from your hand or Discard pile?", romulans)
    if romulan:
        yield from actions.log(romulan)
        yield from actions.gain_specialty("military", 1)


@operation("1SEL06", 2, uses=[A.GAIN_SPECIALTY, A.ATTACK, A.TAKE_INCIDENT])
def thalaron(ctx, actions):
    """ATTACK ACTIVATION: Gain 1 [Military]. Your opponent takes an Incident."""
    yield from actions.gain_specialty("military", 1)
    if (yield from actions.attack()):
        yield from actions.take_incident(opponent=True)
