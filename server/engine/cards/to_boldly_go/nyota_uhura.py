"""2KIRK22 Nyota Uhura (Person). Spec: resources/scans/to_boldly_go/cards/captains/kirk/2KIRK22.md"""

from engine.cards import operation
from engine.ops import SPECIES, A, Spend

from ._util import distinct_traits, has_trait


@operation("2KIRK22", 0, uses=[A.GAIN_CARD], cost=[Spend(dilithium=2)])
def hailing(ctx, actions):
    """PLAY: Spend 2 [Dilithium] to gain a Person/Ally."""
    yield from actions.gain_card(["Person", "Ally"], label="a Person or Ally")


@operation("2KIRK22", 1, uses=[A.GAIN_CARD], cost=[Spend(dilithium=2)], requires=lambda ctx: ctx.track("influence") >= 5)
def first_contact(ctx, actions):
    """PLAY: Requires [Influence] 5. Spend 2 [Dilithium] to gain an Alien, including from the Junk."""
    yield from actions.gain_card(None, lambda i: has_trait(i, "Alien"), "an Alien", from_junk=True)


@operation("2KIRK22", 2, uses=[A.SPEND, A.GAIN_RESOURCE])
def linguist(ctx, actions):
    """ACTIVATION: For each Different Species you have in play, excluding cards with Starfleet (max 3 times): you may
    spend 1 [Dilithium] to gain 1 [Glory]."""
    cards = [i for i in ctx.in_play() if not has_trait(i, "Starfleet")]
    times = min(3, distinct_traits(cards, SPECIES))
    for n in range(1, times + 1):
        if not actions.can_spend(dilithium=1) or not (
                yield from actions.may(f"Spend 1 Dilithium to gain 1 Glory ({n} of {times})?")):
            break
        yield from actions.spend(dilithium=1)
        yield from actions.gain_resource("glory", 1)
