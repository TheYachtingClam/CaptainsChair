"""Khan's Five-Year Mission upgrades. Spec: resources/scans/to_boldly_go/command/khan.md"""

from engine.ops import A, Spend
from engine.upgrades import boost
from engine.upgrades._shared import is_suit

CREW = "khan"


@boost(CREW, "win", 0, moment="before_hand", uses=[A.SCAN_FOR], cost=[Spend(latinum=1)])
def scan_for_an_augment_creature_or_scientist(ctx, actions):
    """BOOST: Before drawing the starting hand, spend 1 [Latinum] to scan for an Augment or a Creature or a
    Scientist."""
    yield from actions.scan_for(lambda i: any(ctx.has(i, t) for t in ("Augment", "Creature", "Scientist")),
                                "an Augment, a Creature or a Scientist")


@boost(CREW, "win", 1, moment="before_hand", uses=[A.FIND, A.ATTACK, A.GIVE])
def give_an_incident(ctx, actions):
    """ATTACK BOOST: Before drawing the starting hand, find an Incident, except in your Reserve deck, and give it to
    your opponent."""
    found, _ = yield from actions.find(lambda i: is_suit(i, "Incident"), "an Incident", exclude_reserve=True)
    if found is not None and (yield from actions.attack()):
        yield from actions.give_incident(found)


@boost(CREW, "loss", 0, moment="before_hand", uses=[A.SCAN_FOR], cost=[Spend(latinum=1)])
def scan_for_an_augment(ctx, actions):
    """BOOST: Before drawing the starting hand, spend 1 [Latinum] to scan for an Augment."""
    yield from actions.scan_for(lambda i: ctx.has(i, "Augment"), "an Augment")


@boost(CREW, "loss", 1, moment="after_hand", uses=[A.DRAW, A.ATTACK, A.TAKE_INCIDENT])
def draw_and_they_take_an_incident(ctx, actions):
    """ATTACK BOOST: After drawing the starting hand, draw a card and your opponent takes an Incident."""
    yield from actions.draw(1)
    if (yield from actions.attack()):
        yield from actions.take_incident(opponent=True)
