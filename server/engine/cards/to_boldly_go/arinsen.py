"""2ALL01 Arin'sen (Ally). Spec: resources/scans/to_boldly_go/cards/ally/2ALL01.md"""

from engine.cards import operation
from engine.ops import A

from ._util import count_traits, others_in_hand


@operation("2ALL01", 0, uses=[A.GAIN_RESOURCE, A.DISCARD, A.LOG], requires=lambda ctx: ctx.track("military") >= 3)
def klingon_tribute(ctx, actions):
    """PLAY: Requires [Military] 3. For each Klingon you have in play (max 5 times): Gain 2 [Dilithium] OR gain 1
    [Latinum] OR discard a card to gain 1 [Glory]. Log this card."""
    times = min(5, count_traits(ctx, "Klingon"))
    for n in range(1, times + 1):
        options = [("dil", "Gain 2 Dilithium"), ("lat", "Gain 1 Latinum")]
        if others_in_hand(ctx):
            options.append(("glory", "Discard a card to gain 1 Glory"))
        choice = yield from actions.choose(f"Klingon {n} of {times}: choose one.", options)
        if choice == "dil":
            yield from actions.gain_resource("dilithium", 2)
        elif choice == "lat":
            yield from actions.gain_resource("latinum", 1)
        else:
            yield from actions.discard(1)
            yield from actions.gain_resource("glory", 1)
    yield from actions.log(ctx.this_card)
