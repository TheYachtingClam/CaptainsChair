"""2SOV21 Sub-Commander T'Pol (Person). Spec: resources/scans/to_boldly_go/cards/captains/soval/2SOV21.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import has_trait, is_suit


@operation("2SOV21", 0, uses=[A.SPEND, A.SCAN_FOR, A.DRAW, A.PROMOTE])
def science_officer(ctx, actions):
    """PLAY: You may spend 2 [Dilithium] to scan for either [Research], or [Influence], or [Military]. You may draw a
    card. You may promote a Person from your hand or Staging Area to Duty Officer (can be this card).
    Ruling: these are Skill icons, not Focus icons."""
    if actions.can_spend(dilithium=2) and (yield from actions.may("Spend 2 Dilithium to scan for a Skill icon?")):
        yield from actions.spend(dilithium=2)
        icon = yield from actions.choose("Scan for which Skill icon?", [("Research", "Research"),
                                                                        ("Influence", "Influence"),
                                                                        ("Military", "Military")])
        yield from actions.scan_for(lambda i: icon in ctx.card(i).skills, f"a card with {icon}")
    if (yield from actions.may("Draw a card?")):
        yield from actions.draw(1)
    people = [i for i in ctx.me.hand + ctx.me.staging if is_suit(i, "Person")]
    person = yield from actions.pick_card("Promote a Person from your hand or Staging Area?", people, optional=True,
                                          none_label="No")
    if person:
        yield from actions.promote(person)


@operation("2SOV21", 1, uses=[A.GAIN_RESOURCE, A.SPEND, A.GAIN_SPECIALTY])
def logic_supply(ctx, actions):
    """RESUPPLY: Gain 1 [Dilithium] OR spend 1 [Dilithium] to gain 1 [Research]."""
    options = [("gain", "Gain 1 Dilithium")] + ([("convert", "Spend 1 Dilithium to gain 1 Research")]
                                                if actions.can_spend(dilithium=1) else [])
    choice = options[0][0] if len(options) == 1 else (yield from actions.choose("T'Pol: choose one.", options))
    if choice == "gain":
        yield from actions.gain_resource("dilithium", 1)
    else:
        yield from actions.spend(dilithium=1)
        yield from actions.gain_specialty("research", 1)


@operation("2SOV21", 2, uses=[A.DISCARD, A.DRAW_FROM_DISCARD],
           cost=[DiscardFromHand(1, lambda ctx, i: has_trait(i, "Human", "Engineer"), "a Human or Engineer")])
def records(ctx, actions):
    """ACTIVATION: Discard a Human/Engineer to draw a Cargo/Directive from your Discard pile."""
    yield from actions.draw_from_discard(lambda i: is_suit(i, "Cargo", "Directive"), "a Cargo or Directive")
