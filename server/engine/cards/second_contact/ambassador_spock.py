"""3PER01 Ambassador Spock (Person, Reward). Spec: resources/scans/second_contact/cards/rewards/3PER01.md"""

from engine import cards as registry
from engine.cards import duty_slots, operation
from engine.ops import A, LogFromHand

from ._util import is_suit, minus_unless_logged

registry.VP_SPECIAL["3PER01"] = minus_unless_logged(2)  # SPECIAL: If not logged, this card scores -2.


@operation("3PER01", 0, uses=[A.LOG, A.GAIN_RESOURCE, A.SCAN_FOR], cost=[LogFromHand()])
def unification(ctx, actions):
    """PLAY: Log a card from your hand to gain 3 [Dilithium]. You may log a beamed card to scan for [Research Focus]."""
    yield from actions.gain_resource("dilithium", 3)
    beamed = [b for host in ctx.in_play(beamed=False) for b in host.beamed]
    card = yield from actions.pick_card("Log a beamed card to scan for a Research Focus card?", beamed, optional=True,
                                        none_label="No")
    if card:
        yield from actions.log(card)
        yield from actions.scan_for(lambda i: ctx.card(i).focus == "Research", "a card with a Research Focus")


@operation("3PER01", 1, uses=[A.GAIN_SPECIALTY], requires=lambda ctx: ctx.track("research") >= 5,
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and is_suit(ctx.event_card, "Encounter") and ctx.track("research") >= 5)
def curiosity(ctx, actions):
    """REACTION: Requires [Research] 5. After putting an Encounter into play, gain 1 [Research]/[Influence]/[Military]."""
    track = yield from actions.choose("Gain 1 on which track?", [(t, t.capitalize()) for t in
                                                                 ("research", "influence", "military")])
    yield from actions.gain_specialty(track, 1)


@duty_slots("3PER01")
def envoy(state, owner, inst):
    """PASSIVE: You may additionally have another Person with Vulcan/Romulan/Ambassador on duty."""
    return [("Vulcan", "Romulan", "Ambassador")]
