"""1KOL23 Krell (Person). Spec: resources/scans/base_game/cards/captains/koloth/1KOL23.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import count_traits, has_trait


@operation("1KOL23", 0, uses=[A.SCAN, A.GAIN_SPECIALTY], cost=[Spend(dilithium=1)])
def gun_runner(ctx, actions):
    """PLAY: Spend 1 [Dilithium] to scan 2 of Cargo. If the gained card has Weapon, gain 1 [Influence]."""
    gained = yield from actions.scan(2, ["Cargo"])
    if gained is not None and has_trait(gained, "Weapon"):
        yield from actions.gain_specialty("influence", 1)


@operation("1KOL23", 1, uses=[A.GAIN_RESOURCE])
def arms_trade(ctx, actions):
    """RESUPPLY: If you have a Weapon in play (excluding your Captain), gain 1 [Latinum], and 1 [Dilithium]. If you
    have 2+ Weapon in play (excluding your Captain), also gain 1 [Glory]."""
    weapons = count_traits(ctx, "Weapon", exclude=ctx.me.captain)
    if weapons >= 1:
        yield from actions.gain_resource("latinum", 1)
        yield from actions.gain_resource("dilithium", 1)
    if weapons >= 2:
        yield from actions.gain_resource("glory", 1)
