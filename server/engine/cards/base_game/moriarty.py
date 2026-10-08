"""1PER16 Moriarty (Person). Spec: resources/scans/base_game/cards/person/1PER16.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait


def _is(ctx, trait):
    return ctx.event_card is not None and ctx.has(ctx.event_card, trait)


@operation("1PER16", 0, uses=[A.SPEND, A.SCAN_FOR, A.ATTACK, A.FORCE, A.DISCARD],
           requires=lambda ctx: ctx.track("research") >= 5)
def take_the_ship(ctx, actions):
    """ATTACK PLAY: Requires [Research] 5. You may spend 2 [Dilithium] to scan for either a Hologram or an Engineer.
    Force your opponent to discard 2 cards."""
    if actions.can_spend(dilithium=2):
        choice = yield from actions.choose("Spend 2 Dilithium to scan for a Hologram or an Engineer?",
                                           [("Hologram", "A Hologram"), ("Engineer", "An Engineer"), ("none", "No")])
        if choice != "none":
            yield from actions.spend(dilithium=2)
            yield from actions.scan_for(lambda i: has_trait(i, choice), f"a {choice}")
    if (yield from actions.attack()) and ctx.opponent is not None:
        yield from actions.discard(2, player=ctx.opponent)


@operation("1PER16", 1, uses=[A.GAIN_RESOURCE, A.DRAW],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and (_is(ctx, "Synthetic") or _is(ctx, "Hologram")))
def self_aware(ctx, actions):
    """REACTION: After putting a Synthetic into play, gain 1 [Glory]. After putting a Hologram into play, draw a card.
    If the card you put in play has both traits, gain both rewards."""
    if _is(ctx, "Synthetic"):
        yield from actions.gain_resource("glory", 1)
    if _is(ctx, "Hologram"):
        yield from actions.draw(1)
