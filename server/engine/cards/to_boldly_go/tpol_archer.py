"""2ARC12 T'Pol (Person). Like Soval's Sub-Commander T'Pol, but the scan costs 1 Dilithium.
Spec: resources/scans/to_boldly_go/cards/captains/archer/2ARC12.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand

from ._util import has_trait, is_suit
from .sub_commander_tpol import logic_supply, records


@operation("2ARC12", 0, uses=[A.SPEND, A.SCAN_FOR, A.DRAW, A.PROMOTE])
def science_officer(ctx, actions):
    """PLAY: You may spend 1 [Dilithium] to scan for either [Research], or [Influence], or [Military]. You may draw a
    card. You may promote a Person from your hand or Staging Area to Duty Officer (can be this card)."""
    if actions.can_spend(dilithium=1) and (yield from actions.may("Spend 1 Dilithium to scan for a Skill icon?")):
        yield from actions.spend(dilithium=1)
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


operation("2ARC12", 1, uses=[A.GAIN_RESOURCE, A.SPEND, A.GAIN_SPECIALTY])(logic_supply)
operation("2ARC12", 2, uses=[A.DISCARD, A.DRAW_FROM_DISCARD],
          cost=[DiscardFromHand(1, lambda ctx, i: has_trait(i, "Human", "Engineer"), "a Human or Engineer")])(records)
