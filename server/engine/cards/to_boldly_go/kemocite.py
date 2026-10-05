"""2CAR10 Kemocite (Cargo). Spec: resources/scans/to_boldly_go/cards/cargo/2CAR10.md"""

from engine.cards import operation
from engine.ops import A, DismissFromPlay, Spend

from ._util import has_trait, ships


def _weapon(i) -> bool:
    return has_trait(i, "Weapon")


@operation("2CAR10", 0, uses=[A.FIND, A.FREE_PLAY, A.TAKE_INCIDENT],
           requires=lambda ctx: any(_weapon(i) and i is not ctx.this_card
                                    for i in ctx.me.hand + ctx.me.draw + ctx.me.discard + ctx.me.reserve))
def arm(ctx, actions):
    """PLAY: Find and free play a Weapon. If the card was found in your Reserve deck, take an Incident."""
    weapon, zone = yield from actions.find(_weapon, "a Weapon")
    if weapon and actions.free_play_candidates(lambda i: i is weapon):
        yield from actions.free_play(weapon)
    if zone == "reserve":
        yield from actions.take_incident()


@operation("2CAR10", 1, uses=[A.RECALL, A.DRAW],
           cost=[DismissFromPlay(lambda ctx, i: i in ships(ctx), "one of your deployed Ships")])
def scuttle(ctx, actions):
    """PLAY: Dismiss a deployed Ship to recall a non-Time Travel card from your Staging Area and draw 2 cards."""
    cards = [i for i in ctx.me.staging if not has_trait(i, "Time Travel")]
    card = yield from actions.pick_card("Recall which card from your Staging Area?", cards)
    if card:
        yield from actions.recall(card)
    yield from actions.draw(2)


@operation("2CAR10", 2, uses=[A.SCAN_FOR], cost=[Spend(dilithium=1)])
def scan_weapon(ctx, actions):
    """PLAY: Spend 1 [Dilithium] to scan for Weapon."""
    yield from actions.scan_for(_weapon, "a Weapon")


