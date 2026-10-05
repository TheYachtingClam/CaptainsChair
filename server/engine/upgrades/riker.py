"""Riker's Five-Year Mission upgrades. Spec: resources/scans/second_contact/command/riker.md"""

from engine.ops import A
from engine.upgrades import boost
from engine.upgrades._shared import find_and_promote_person, is_suit

CREW = "riker"


@boost(CREW, "win", 0, moment="before_hand", uses=[A.FIND, A.FREE_PLAY])
def free_play_a_location(ctx, actions):
    """BOOST: Before drawing the starting hand, find a Location, except in your Reserve deck, and immediately free
    play it."""
    found, _ = yield from actions.find(lambda i: is_suit(i, "Location"), "a Location", exclude_reserve=True)
    if found is not None:
        yield from actions.free_play(found)


@boost(CREW, "win", 1, moment="before_hand", uses=[A.FIND, A.PROMOTE])
def promote_a_person_before(ctx, actions):
    """BOOST: Before drawing the starting hand, find a Person, except in your Reserve deck, and promote them to Duty
    Officer."""
    yield from find_and_promote_person(ctx, actions)


@boost(CREW, "loss", 0, moment="after_hand", uses=[A.FIND, A.SPEND, A.FREE_PLAY, A.WARP])
def two_ship_options(ctx, actions):
    """BOOST: After drawing the starting hand, choose 2 of the following: find a Ship, except in your Reserve deck
    OR spend 1 [Latinum] to free play a Ship OR warp a Ship."""
    options = {"find": "Find a Ship, except in your Reserve deck", "play": "Spend 1 Latinum to free play a Ship",
               "warp": "Warp a Ship"}
    for n in (1, 2):
        ships_in_hand = actions.free_play_candidates(lambda i: is_suit(i, "Ship"))
        deployed = [s for s in ctx.me.fleet if is_suit(s, "Ship") or ctx.card(s).ship_token]
        able = {"find": True, "play": ctx.me.latinum >= 1 and bool(ships_in_hand), "warp": bool(deployed)}
        choices = [(k, v) for k, v in options.items() if able[k]]
        if not choices:
            return
        pick = yield from actions.choose(f"Choose option {n} of 2.", choices)
        del options[pick]
        if pick == "find":
            yield from actions.find(lambda i: is_suit(i, "Ship"), "a Ship", exclude_reserve=True)
        elif pick == "play":
            ship = yield from actions.pick_card("Free play which Ship?", ships_in_hand)
            yield from actions.spend(latinum=1)
            yield from actions.free_play(ship)
        else:
            ship = deployed[0] if len(deployed) == 1 else (yield from actions.pick_card("Warp which Ship?", deployed))
            yield from actions.warp(ship)


@boost(CREW, "loss", 1, moment="after_hand", uses=[A.FIND, A.PROMOTE])
def promote_a_person_after(ctx, actions):
    """BOOST: After drawing the starting hand, find a Person, except in your Reserve deck, and promote them to Duty
    Officer."""
    yield from find_and_promote_person(ctx, actions)
