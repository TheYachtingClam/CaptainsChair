"""3RIK05 William Boimler, Lt. jg (Person, Development). Spec: resources/scans/second_contact/cards/captains/william riker/3RIK05.md"""

from engine.cards import development_cost, hand_size_modifier, operation
from engine.ops import A, DiscardFromHand, EffectCost, Spend

from ._util import has_trait, is_suit, ships


def _findable_people(ctx):
    me = ctx.me
    return [i for i in me.hand + me.draw + me.discard + me.reserve if is_suit(i, "Person")]


def _beam_three(ctx, actions):
    """Find 3 Person and beam them to the same Ship."""
    ship = yield from actions.pick_card("Beam 3 Persons to which Ship?", ships(ctx))
    for n in (1, 2, 3):
        person, _ = yield from actions.find(lambda i: is_suit(i, "Person"), f"a Person ({n} of 3)")
        if person is None:
            break
        yield from actions.beam(person, ship)


development_cost("3RIK05", Spend(dilithium=1, latinum=1), EffectCost(
    lambda ctx: bool(ships(ctx)) and len(_findable_people(ctx)) >= 3, _beam_three, (A.FIND, A.BEAM),
    "find 3 Person and beam them to the same Ship"))


@operation("3RIK05", 0, uses=[A.DISCARD, A.SCAN, A.DRAW, A.DRAW_FROM_DISCARD], cost=[DiscardFromHand(1)],
           trigger=lambda ctx, ev: ev["kind"] == "exhaust" and ev["seat"] == ctx.me.seat
           and ev.get("uid") == ctx.me.captain.uid)
def mixology(ctx, actions):
    """SUPPORT: After exhausting your Captain, discard a card to scan 1 of Cargo. If the gained card is Beverage, draw
    it."""
    gained = yield from actions.scan(1, ["Cargo"])
    if gained is None or not has_trait(gained, "Beverage"):
        return
    if gained in ctx.me.discard:
        yield from actions.draw_from_discard(lambda i: i.uid == gained.uid, ctx.name(gained))
    elif ctx.me.draw and ctx.me.draw[0] is gained:
        yield from actions.draw(1)


@operation("3RIK05", 1, uses=[A.ADJUST_HAND_SIZE])
def two_boimlers(ctx, actions):
    """CLEAN-UP: If Brad Boimler, Lt. jg is in play, temporarily increase your hand size by 1."""
    if ctx.count_in_play(lambda i: i.card == "3RIK14"):
        yield from actions.adjust_hand_size(1)


@hand_size_modifier("3RIK05")
def bigger_hand(state, owner, size):
    """PASSIVE: Increase your hand size by 1."""
    return size + 1
