"""1PER21 Sakonna (Person). Spec: resources/scans/base_game/cards/person/1PER21.md"""

from engine.cards import operation
from engine.ops import A

from ._util import count_traits, has_trait, others_in_hand


def _weapon(i):
    return has_trait(i, "Weapon")


@operation("1PER21", 0, uses=[A.SPEND, A.GAIN_SPECIALTY, A.DISCARD, A.FIND])
def arms_deal(ctx, actions):
    """PLAY: You may spend 1 [Latinum] to gain 1 [Influence] and 1 [Military]. You may discard a Weapon to gain 1
    [Influence]/[Military]. You may find a Ferengi."""
    if actions.can_spend(latinum=1) and (yield from actions.may("Spend 1 Latinum to gain 1 Influence and 1 Military?")):
        yield from actions.spend(latinum=1)
        yield from actions.gain_specialty("influence", 1)
        yield from actions.gain_specialty("military", 1)
    if others_in_hand(ctx, _weapon) and (yield from actions.may("Discard a Weapon to gain 1 Influence or Military?")):
        yield from actions.discard(1, pred=_weapon, label="a Weapon")
        track = yield from actions.choose("Gain 1 on which track?", [("influence", "Influence"), ("military", "Military")])
        yield from actions.gain_specialty(track, 1)
    if (yield from actions.may("Find a Ferengi?")):
        yield from actions.find(lambda i: has_trait(i, "Ferengi"), "a Ferengi")


@operation("1PER21", 1, uses=[A.SCAN_FOR, A.DRAW], requires=lambda ctx: False)
def badlands(ctx, actions):
    """PLAY: If you have a Ship at the Badlands, scan for Weapon and draw a card.
    Ruling: the Badlands is a joke; no Location has that name, so this is never offered."""
    yield from actions.scan_for(_weapon, "a Weapon")
    yield from actions.draw(1)


@operation("1PER21", 2, uses=[A.REVEAL, A.GAIN_RESOURCE, A.GAIN_ACTION], requires=lambda ctx: ctx.track("military") >= 4)
def smuggle(ctx, actions):
    """RESUPPLY: Requires [Military] 4. Reveal your hand. If you have a Weapon in your hand, gain 1 [Latinum]. If you
    have a Weapon in your hand and a Weapon in play, additionally gain an [Action]."""
    yield from actions.reveal(list(ctx.me.hand))
    if any(_weapon(i) for i in ctx.me.hand):
        yield from actions.gain_resource("latinum", 1)
        if count_traits(ctx, "Weapon"):
            yield from actions.gain_action(1)
