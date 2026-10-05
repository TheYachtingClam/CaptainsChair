"""3FRE23 Bradward Boimler (Person). His PLAY and SUPPORT are registered with Riker's Brad Boimler
(engine/cards/second_contact/brad_boimler.py). Spec: resources/scans/second_contact/cards/captains/freeman/3FRE23.md"""

from engine.cards import operation
from engine.ops import A, EffectCost, TakeIncidentCost

from ._util import has_trait, table_of


def _lower_deckers(ctx):
    """Your in-play Lower Deckers that can be dismissed (not in the Staging Area, KW-DSM-04)."""
    table = [i for i in table_of(ctx.me) if i is not ctx.me.captain]
    cards = table + [b for host in table for b in host.beamed]
    return [i for i in cards if has_trait(i, "Lower Decker")]


def _dismiss_four(ctx, actions):
    for n in range(1, 5):
        card = yield from actions.pick_card(f"Dismiss which Lower Decker ({n} of 4)?", _lower_deckers(ctx))
        yield from actions.dismiss(card)


@operation("3FRE23", 2, uses=[A.DISMISS, A.TAKE_INCIDENT, A.TAKE_ENCOUNTER],
           cost=[EffectCost(lambda ctx: len(_lower_deckers(ctx)) >= 4, _dismiss_four, (A.DISMISS,),
                            "dismiss 4 Lower Decker"), TakeIncidentCost()])
def away_mission(ctx, actions):
    """ACTIVATION: Dismiss 4 Lower Decker (one of them can be this card) and take an Incident to take the top
    Encounter."""
    yield from actions.take_encounter()
