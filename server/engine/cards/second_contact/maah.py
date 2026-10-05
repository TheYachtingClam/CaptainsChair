"""3PER12 Ma'ah (Person). Spec: resources/scans/second_contact/cards/person/3PER12.md"""

from engine.cards import operation
from engine.ops import A, DismissDutyOfficer, LogFromHand

from ._util import has_trait, is_suit


@operation("3PER12", 0, uses=[A.DISMISS, A.GAIN_SPECIALTY, A.GAIN_RESOURCE], cost=[DismissDutyOfficer()])
def challenge(ctx, actions):
    """PLAY: Dismiss a Duty Officer to gain 1 [Influence], 1 [Military], and 1 [Glory]."""
    yield from actions.gain_specialty("influence", 1)
    yield from actions.gain_specialty("military", 1)
    yield from actions.gain_resource("glory", 1)


@operation("3PER12", 2, uses=[A.LOG, A.GAIN_SPECIALTY, A.DRAW],
           cost=[LogFromHand(lambda ctx, i: has_trait(i, "Klingon", "Shady", "Lower Decker"),
                             "a Klingon, Shady or Lower Decker", ("hand", "discard"))])
def honour(ctx, actions):
    """ACTIVATION: Log a Klingon / Shady / Lower Decker from your hand or Discard pile to gain 1 [Influence] and draw
    2 cards."""
    yield from actions.gain_specialty("influence", 1)
    yield from actions.draw(2)


@operation("3PER12", 1, uses=[A.GAIN_CARD, A.DISCARD, A.TAKE_INCIDENT, A.SPEND],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and has_trait(ctx.event_card, "Klingon"))
def reinforcements(ctx, actions):
    """SUPPORT: After putting a Klingon into play, gain a Ship. Then, either spend an [Action] and discard an Incident
    OR take an Incident. Ruling: Ma'ah himself is a Klingon put into play, so he can start a chain (REQ-EXP-35)."""
    yield from actions.gain_card(["Ship"], label="a Ship")
    incidents = [i for i in ctx.me.hand if is_suit(i, "Incident")]
    options = ([("discard", "Spend an Action and discard an Incident")] if incidents and ctx.me.actions > 0 else []) \
        + [("take", "Take an Incident")]
    choice = options[0][0] if len(options) == 1 else (yield from actions.choose("Ma'ah: choose one.", options))
    if choice == "discard":
        yield from actions.spend(actions=1)
        yield from actions.discard(1, pred=lambda i: is_suit(i, "Incident"), label="an Incident")
    else:
        yield from actions.take_incident()
