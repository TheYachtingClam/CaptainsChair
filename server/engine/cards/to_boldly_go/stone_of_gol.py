"""2ENC07 Stone of Gol (Encounter). Spec: resources/scans/to_boldly_go/cards/encounter/2ENC07.md"""

from engine.cards import operation
from engine.ops import A

from ._util import count_traits, has_trait


@operation("2ENC07", 0, uses=[A.ATTACK, A.FORCE, A.DISMISS, A.EXHAUST, A.GAIN_RESOURCE])
def psionic_weapon(ctx, actions):
    """ATTACK PLAY: For each Duty Officer your opponent has in play, force them to either: dismiss it OR exhaust it and
    you gain 1 [Glory]. Ruling: an exhausted Duty Officer cannot be exhausted again, so it is dismissed (KW-FORCE-03).
    Cadet: the virtual opponent dismisses its Duty Officer, which gives you nothing."""
    opp = ctx.opponent
    if not (yield from actions.attack()) or opp is None:
        return
    for officer in list(opp.duty):
        if officer.exhausted:
            yield from actions.dismiss(officer)
            continue
        choice = yield from actions.choose(f"Stone of Gol: dismiss {ctx.name(officer)}, or exhaust it (your opponent "
                                           "gains 1 Glory)?", [("dismiss", "Dismiss it"),
                                                               ("exhaust", "Exhaust it; opponent gains 1 Glory")],
                                           seat=opp.seat)
        if choice == "dismiss":
            yield from actions.dismiss(officer)
        else:
            yield from actions.exhaust(officer)
            yield from actions.gain_resource("glory", 1)


@operation("2ENC07", 1, uses=[A.ATTACK, A.TAKE_INCIDENT, A.GAIN_CARD, A.FREE_PLAY])
def ancient_power(ctx, actions):
    """ATTACK PLAY: Your opponent takes an Incident. Gain an Attack, including from the Junk. If you do, and you have
    a Telepath in play, you may free play the gained card."""
    if (yield from actions.attack()):
        yield from actions.take_incident(opponent=True)
    gained = yield from actions.gain_card(None, lambda i: has_trait(i, "Attack"), "an Attack", from_junk=True)
    if gained and count_traits(ctx, "Telepath") and actions.free_play_candidates(lambda i: i is gained, cards=[gained]):
        if (yield from actions.may(f"Free play {ctx.name(gained)}?")):
            yield from actions.free_play(gained)
