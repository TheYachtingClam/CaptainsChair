"""3CAR03 Protocol 12 (Cargo). Spec: resources/scans/second_contact/cards/cargo/3CAR03.md
The SPECIAL (Doctors treated as Augment) arrives in Step 5."""

from engine.cards import operation
from engine.ops import A, LogFromHand, TakeIncidentCost

from ._util import count_traits, is_suit


@operation("3CAR03", 0, uses=[A.SEND_AWAY_TEAM, A.GAIN_RESOURCE], requires=lambda ctx: ctx.track("military") >= 5)
def deploy_medics(ctx, actions):
    """PLAY: Requires [Military] 5. For each Doctor you have in play (excluding this card, max 3), send an [Away
    Team] to a Location. If you sent 3, gain 1 [Glory]."""
    n = min(3, count_traits(ctx, "Doctor", exclude=ctx.this_card))
    sent = 0
    for _ in range(n):
        loc = yield from actions.send_away_team(1)
        if loc is None:
            break
        sent += 1
    if sent == 3:
        yield from actions.gain_resource("glory", 1)


@operation("3CAR03", 1, uses=[A.TAKE_INCIDENT, A.LOG, A.GAIN_SPECIALTY],
           cost=[TakeIncidentCost(), LogFromHand(lambda ctx, i: is_suit(i, "Person", "Directive"), "a Person or Directive",
                                                 ("hand", "play"))])
def classified(ctx, actions):
    """PLAY: Take an Incident and log a Person/Directive from your hand or in play to gain 1 [Military]."""
    yield from actions.gain_specialty("military", 1)

