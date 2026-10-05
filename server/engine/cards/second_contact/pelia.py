"""3PIK08 Pelia (Person, Development). Spec: resources/scans/second_contact/cards/captains/pike/3PIK08.md"""

from engine.cards import development_cost, operation, trait_modifier
from engine.ops import A, DiscardFromHand, Spend, SpendUnless, card

from ._util import is_suit, table_of

development_cost("3PIK08", SpendUnless(Spend(latinum=3), lambda ctx: any(i.card == "3PIK20" for i in ctx.me.log)))


@operation("3PIK08", 0, uses=[A.FIND, A.FREE_PLAY])
def tinkerer(ctx, actions):
    """PLAY: You may find and free play a Cargo."""
    found, _ = yield from actions.find(lambda i: is_suit(i, "Cargo"), "a Cargo", optional=True)
    if found and found in actions.free_play_candidates(lambda i: i.uid == found.uid):
        yield from actions.free_play(found)


@operation("3PIK08", 1, uses=[A.DISCARD, A.GAIN_CARD, A.SPEND, A.DRAW, A.GAIN_RESOURCE], cost=[DiscardFromHand(1)])
def salvage(ctx, actions):
    """ACTIVATION: Discard a card to gain a Cargo from the Junk. You may spend 1 [Latinum] to draw a card and gain 1
    [Glory]."""
    yield from actions.gain_card(["Cargo"], label="a Cargo from the Junk", only_junk=True)
    if actions.can_spend(latinum=1) and (yield from actions.may("Spend 1 Latinum to draw a card and gain 1 Glory?")):
        yield from actions.spend(latinum=1)
        yield from actions.draw(1)
        yield from actions.gain_resource("glory", 1)


@trait_modifier("3PIK08", staging="both")
def old_hand(state, owner, inst, target):
    """SPECIAL: While this card is in play (excluding beamed) and you have another Engineer in play, this card is
    additionally treated as Wildcard."""
    if target is not inst:
        return set()
    others = [i for i in [*table_of(owner), *owner.staging] if i is not inst]
    others += [b for host in others for b in host.beamed]
    return {"Wildcard"} if any("Engineer" in card(i).traits for i in others) else set()
