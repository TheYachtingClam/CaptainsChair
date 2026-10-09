"""1SHR03 Aenar (Ally, Development). Spec: resources/scans/base_game/cards/captains/shran/1SHR03.md"""

from engine.cards import development_cost, operation
from engine.ops import A, EffectCost

from ._util import has_trait


def _weapons(ctx):
    me = ctx.me
    return [i for i in me.hand + me.draw + me.discard + me.reserve if has_trait(i, "Weapon")]


def _find_and_log_a_weapon(ctx, actions):
    weapon, _ = yield from actions.find(lambda i: has_trait(i, "Weapon"), "a Weapon, to log it")
    if weapon is not None:
        yield from actions.log(weapon)


development_cost("1SHR03", EffectCost(lambda ctx: bool(_weapons(ctx)), _find_and_log_a_weapon, (A.FIND, A.LOG),
                                      "find a Weapon and log it"))


@operation("1SHR03", 0, uses=[A.DRAW, A.LOG, A.DISCARD, A.GAIN_SPECIALTY])
def insight(ctx, actions):
    """PLAY: Draw 3 cards. You may log one of the drawn cards. You may discard one of the drawn cards to gain 1
    [Influence]."""
    before = [i.uid for i in ctx.me.hand]
    yield from actions.draw(3)
    drawn = lambda: [i for i in ctx.me.hand if i.uid not in before]  # noqa: E731
    card = yield from actions.pick_card("Log one of the drawn cards?", drawn(), optional=True, none_label="No")
    if card:
        yield from actions.log(card)
    card = yield from actions.pick_card("Discard one of the drawn cards to gain 1 Influence?", drawn(), optional=True,
                                        none_label="No")
    if card:
        yield from actions.discard(1, pred=lambda i: i.uid == card.uid)
        yield from actions.gain_specialty("influence", 1)
