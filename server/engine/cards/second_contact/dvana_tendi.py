"""3FRE14 D'Vana Tendi (Person). Spec: resources/scans/second_contact/cards/captains/freeman/3FRE14.md"""

from engine import cards as registry
from engine.cards import duty_slots, operation
from engine.ops import A, Spend

from ._util import has_trait

TRACKS = ("research", "influence", "military")
# PASSIVE: You may spend [Latinum] as if it was [Dilithium] and vice versa.
registry.RESOURCES_INTERCHANGEABLE.add("3FRE14")


@duty_slots("3FRE14")
def extra_starfleet(state, owner, inst):
    """PASSIVE: You may additionally have another Person with Starfleet on duty."""
    return ["Starfleet"]


@operation("3FRE14", 0, uses=[A.SCAN_FOR, A.FREE_PLAY], cost=[Spend(latinum=1)],
           requires=lambda ctx: ctx.track("influence") >= 5)
def orion_contacts(ctx, actions):
    """PLAY: Requires [Influence] 5. Spend 1 [Latinum] to scan for Orion and free play the gained card."""
    gained = yield from actions.scan_for(lambda i: has_trait(i, "Orion"), "an Orion")
    if gained is not None and gained in actions.free_play_candidates(lambda i: i.uid == gained.uid,
                                                                     ("hand", "discard", "draw")):
        yield from actions.free_play(gained)


@operation("3FRE14", 1, uses=[A.GAIN_SPECIALTY, A.PROMOTE],
           trigger=lambda ctx, ev: ev["kind"] == "promote" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and has_trait(ctx.event_card, "Lower Decker"))
def science_buddy(ctx, actions):
    """SUPPORT: After promoting a Lower Decker, gain 2 [Research]/[Influence]/[Military] and you may promote this card
    to Duty Officer."""
    track = yield from actions.choose("Gain 2 on which track?", [(t, t.capitalize()) for t in TRACKS])
    yield from actions.gain_specialty(track, 2)
    if ctx.this_card in ctx.me.staging and (yield from actions.may("Promote D'Vana Tendi to Duty Officer?")):
        yield from actions.promote(ctx.this_card)
