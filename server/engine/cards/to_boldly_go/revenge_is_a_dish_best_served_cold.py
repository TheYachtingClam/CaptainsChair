"""2KHA10 Revenge Is a Dish Best Served Cold (Directive, Development). Spec: resources/scans/to_boldly_go/cards/captains/kahn/2KHA10.md"""

from engine.cards import VP_SPECIAL, development_cost, operation
from engine.ops import A, Condition, DiscardFromHand, Spend

from ._util import has_trait, is_suit, owned_cards, virtual

development_cost("2KHA10", Spend(latinum=1),
                 Condition(lambda ctx: any(i.card == "2KHA13" for i in ctx.me.log), "have Marla McGivers logged"))


def _penalty(state, player, inst):
    """SPECIAL: During scoring, each of your Incident scores an additional -1 VP. It counts for whoever owns this
    card at the end, which is why its second PLAY gives it away."""
    return -sum(1 for i in owned_cards(player) if is_suit(i, "Incident"))


VP_SPECIAL["2KHA10"] = _penalty


@operation("2KHA10", 0, uses=[A.GAIN_RESOURCE, A.ATTACK, A.FORCE, A.FIND, A.LOG, A.MARK_TRAIT])
def old_scores(ctx, actions):
    """ATTACK PLAY: Gain 1 [Glory]. Force your opponent to find any card, and log it. You may select a card in their
    Discard pile and mark one trait of it. Cadet Training: you may mark a trait from a card in the Junk instead
    (REQ-CD-KHN-10)."""
    yield from actions.gain_resource("glory", 1)
    opp = ctx.opponent
    if (yield from actions.attack()) and opp is not None:
        found, _ = yield from actions.find(lambda i: True, "any card (it will be logged)", player=opp)
        if found is not None:
            yield from actions.log(found)
    pile = ctx.state.junk if virtual(ctx) else (opp.discard if opp is not None else [])
    where = "the Junk" if virtual(ctx) else "their Discard pile"
    cards = [i for i in pile if ctx.can_mark(i)]
    chosen = yield from actions.pick_card(f"Mark one trait of a card in {where}?", cards, optional=True,
                                          none_label="Do not mark")
    if chosen is not None:
        yield from actions.mark_trait(chosen)


@operation("2KHA10", 1, uses=[A.ATTACK, A.GIVE, A.FORCE, A.LOG, A.DESTROY, A.GAIN_RESOURCE],
           cost=[DiscardFromHand(1, lambda ctx, i: has_trait(i, "Augment"), "an Augment")])
def served_cold(ctx, actions):
    """ATTACK PLAY: Discard an Augment to give this card and optionally an Incident to your opponent, and force them to
    log the card(s) given. Cadet Training: destroy both cards and gain 4 [Glory] instead (REQ-CD-KHN-10)."""
    incident = yield from actions.pick_card("Give an Incident with this card?", ctx.hand_incidents(), optional=True,
                                            none_label="No Incident")
    if not (yield from actions.attack()):
        return
    this = ctx.this_card
    if virtual(ctx):
        yield from actions.destroy(this)
        if incident is not None:
            yield from actions.destroy(incident)
        yield from actions.gain_resource("glory", 4)
        return
    yield from actions.give(this)
    yield from actions.log(this)
    if incident is not None:
        yield from actions.give_incident(incident)
        yield from actions.log(incident)
