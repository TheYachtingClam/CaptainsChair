"""1SIS23 Kira Nerys (Person). Spec: resources/scans/base_game/cards/captains/sisko/1SIS23.md"""

from engine.cards import operation
from engine.ops import A

PEOPLE_OF_BAJOR = "1SIS12"


@operation("1SIS23", 0, uses=[A.FIND, A.ATTACK, A.DISMISS, A.PROMOTE])
def resistance(ctx, actions):
    """ATTACK PLAY: Find People of Bajor and dismiss an opponent Cardassian/Dominion (of your choice). Promote this
    card to Duty Officer. A card in their Staging Area, and their Captain, cannot be dismissed."""
    yield from actions.find(lambda i: i.card == PEOPLE_OF_BAJOR, "People of Bajor")
    opp = ctx.opponent
    if (yield from actions.attack()) and opp is not None:
        targets = [i for i in ctx.in_play(opp) if i not in opp.staging and i is not opp.captain
                   and ctx.traits(i) & {"Cardassian", "Dominion"}]
        target = yield from actions.pick_card("Dismiss which opponent Cardassian or Dominion?", targets)
        if target:
            yield from actions.dismiss(target)
    yield from actions.promote(ctx.this_card)


@operation("1SIS23", 1, uses=[A.GAIN_SPECIALTY, A.GAIN_RESOURCE])
def liaison(ctx, actions):
    """PLAY: Gain 3 [Military] and 1 [Glory]. Your opponent gains 1 [Influence]."""
    yield from actions.gain_specialty("military", 3)
    yield from actions.gain_resource("glory", 1)
    if ctx.opponent is not None:
        yield from actions.gain_specialty("influence", 1, player=ctx.opponent)


@operation("1SIS23", 2, uses=[A.DRAW, A.GAIN_RESOURCE],
           trigger=lambda ctx, ev: ev["kind"] == "take_control" and ev["seat"] != ctx.me.seat and ev["seat"] >= 0)
def vigilance(ctx, actions):
    """REACTION: After your opponent takes control of a Location, draw a card and gain 1 [Dilithium]."""
    yield from actions.draw(1)
    yield from actions.gain_resource("dilithium", 1)
