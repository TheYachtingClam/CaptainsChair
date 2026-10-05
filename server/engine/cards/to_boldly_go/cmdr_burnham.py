"""2GEO13 Cmdr. Burnham (Person). Spec: resources/scans/to_boldly_go/cards/captains/georgiou/2GEO13.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import has_trait, species_of


@operation("2GEO13", 0, uses=[A.DISMISS, A.ATTACK, A.FORCE, A.LOG, A.GAIN_RESOURCE],
           requires=lambda ctx: ctx.track("military") > ctx.track("research"))
def attack_duty_officers(ctx, actions):
    """ATTACK PLAY: Requires Military > Research: Dismiss a Duty Officer. Force your opponent to either: log
    (one of) their Duty Officer(s) OR dismiss (one of) their Duty Officer(s) and you gain 3 Glory.
    Ruling: the first Duty Officer is your own, dismissed if you have one; with none the attack still resolves."""
    if ctx.me.duty:
        own = yield from actions.pick_card("Dismiss one of your Duty Officers.", list(ctx.me.duty))
        yield from actions.dismiss(own)
    opp = ctx.opponent
    if not (yield from actions.attack()):
        return
    if opp is None or not opp.duty:
        # Cadet Training: the virtual opponent has a Duty Officer and chooses to log it, so nothing happens
        # for you (REQ-CTM-12; ruling assumed, see OPEN_QUESTIONS.md).
        return
    choice = yield from actions.choose(
        "Cmdr. Burnham attacks: log one of your Duty Officers, or dismiss one and your opponent gains 3 Glory?",
        [("log", "Log a Duty Officer"), ("dismiss", "Dismiss a Duty Officer (opponent gains 3 Glory)")], seat=opp.seat)
    target = yield from actions.pick_card("Which Duty Officer?", list(opp.duty), seat=opp.seat)
    if choice == "log":
        yield from actions.log(target)
    else:
        yield from actions.dismiss(target)
        yield from actions.gain_resource("glory", 3)


@operation("2GEO13", 1, uses=[A.SCAN_FOR],
           cost=[DiscardFromHand(1, lambda ctx, i: not has_trait(i, "Starfleet"), "a non-Starfleet card")],
           requires=lambda ctx: ctx.track("research") > ctx.track("military"))
def scan_matching_species(ctx, actions):
    """PLAY: Requires Research > Military: Discard a non-Starfleet card to scan for Any Species matching the
    discarded card."""
    discarded = actions.paid[0]
    wanted = species_of(discarded)
    yield from actions.scan_for(lambda i: bool(species_of(i) & wanted), "a card sharing a species with " + ctx.name(discarded))


@operation("2GEO13", 2, uses=[A.TAKE_INCIDENT, A.DRAW, A.GAIN_SPECIALTY])
def resupply(ctx, actions):
    """RESUPPLY: Take an Incident. Draw a card. Gain 1 Research/Military."""
    yield from actions.take_incident()
    yield from actions.draw(1)
    track = yield from actions.choose("Gain 1 Research or 1 Military?", [("research", "Research"), ("military", "Military")])
    yield from actions.gain_specialty(track, 1)
