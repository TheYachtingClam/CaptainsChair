"""2REB19 Grebnedlog (Person). Spec: resources/scans/to_boldly_go/cards/captains/rebner/2REB19.md"""

from engine.cards import operation
from engine.ops import A, Spend

from ._util import has_trait, is_suit, wearing


@operation("2REB19", 0, uses=[A.GAIN_CARD])
def hire(ctx, actions):
    """PLAY: Gain a Person."""
    yield from actions.gain_card(["Person"], label="a Person")


@operation("2REB19", 1, uses=[A.SCAN_FOR], cost=[Spend(dilithium=1)], requires=lambda ctx: ctx.track("military") >= 3)
def engineers(ctx, actions):
    """PLAY: Requires [Military] 3. Spend 1 [Dilithium] to scan for an Engineer."""
    yield from actions.scan_for(lambda i: has_trait(i, "Engineer"), "an Engineer")


@operation("2REB19", 2, uses=[A.SCAN_FOR], cost=[Spend(latinum=1)], requires=lambda ctx: ctx.track("military") >= 6)
def experts(ctx, actions):
    """PLAY: Requires [Military] 6. Spend 1 [Latinum] to scan for either a Shady or a Scientist."""
    trait = yield from actions.choose("Scan for which?", [("Shady", "Shady"), ("Scientist", "Scientist")])
    yield from actions.scan_for(lambda i: has_trait(i, trait), f"a {trait}")


@operation("2REB19", 3, uses=[A.DISCARD, A.GAIN_RESOURCE, A.GAIN_SPECIALTY])
def sell_off(ctx, actions):
    """ACTIVATION: You may discard a Person to gain 3 [Dilithium]. If the discarded card is Engineer, gain 1 [Glory].
    If Grebnedlog is wearing a Helmet, gain 1 [Military]."""
    out = yield from actions.discard(1, pred=lambda i: is_suit(i, "Person"), label="a Person to gain 3 Dilithium",
                                     optional=True)
    if out:
        yield from actions.gain_resource("dilithium", 3)
        if has_trait(out[0], "Engineer"):
            yield from actions.gain_resource("glory", 1)
    if wearing(ctx.this_card):
        yield from actions.gain_specialty("military", 1)
