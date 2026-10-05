"""2PER25 Va'al Trask (Person). Spec: resources/scans/to_boldly_go/cards/person/2PER25.md"""

from engine.cards import operation
from engine.ops import A

from ._util import has_trait, is_suit, others_in_hand


@operation("2PER25", 0, uses=[A.DISCARD, A.SCAN_FOR, A.LOG, A.GAIN_RESOURCE, A.PROMOTE])
def tactical_officer(ctx, actions):
    """PLAY: You may discard a Starfleet to scan for a Weapon. You may log a Person from your hand or Discard pile. If
    you do both, gain 1 [Glory], and you may promote this card to Duty Officer."""
    scanned = logged = False
    if others_in_hand(ctx, lambda i: has_trait(i, "Starfleet")) and (
            yield from actions.may("Discard a Starfleet to scan for a Weapon?")):
        yield from actions.discard(1, pred=lambda i: has_trait(i, "Starfleet"), label="a Starfleet")
        yield from actions.scan_for(lambda i: has_trait(i, "Weapon"), "a Weapon")
        scanned = True
    people = [i for i in ctx.me.hand + ctx.me.discard if is_suit(i, "Person") and i is not ctx.this_card]
    person = yield from actions.pick_card("Log a Person from your hand or Discard pile?", people, optional=True,
                                          none_label="No")
    if person:
        yield from actions.log(person)
        logged = True
    if scanned and logged:
        yield from actions.gain_resource("glory", 1)
        if ctx.this_card in ctx.me.staging and (yield from actions.may("Promote Va'al Trask to Duty Officer?")):
            yield from actions.promote(ctx.this_card)


@operation("2PER25", 1, uses=[A.DISCARD, A.SPEND, A.DRAW_FROM_DISCARD])
def patrol(ctx, actions):
    """RESUPPLY: For each [Away Team] you or your opponent have on neutral Location, either: discard the top card of
    your Draw deck OR spend 1 [Dilithium] to draw a card from your Discard pile."""
    teams = sum(sum(loc.away.values()) for loc in ctx.state.neutral)
    for n in range(1, teams + 1):
        options = [("top", "Discard the top card of your deck")]
        if actions.can_spend(dilithium=1) and ctx.me.discard:
            options.append(("draw", "Spend 1 Dilithium to take a card from your Discard pile"))
        choice = yield from actions.choose(f"Va'al Trask ({n} of {teams}): choose one.", options)
        if choice == "top":
            yield from actions.discard_top()
        else:
            yield from actions.spend(dilithium=1)
            yield from actions.draw_from_discard()
