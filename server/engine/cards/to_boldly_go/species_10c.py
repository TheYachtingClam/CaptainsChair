"""2ENC06 Species 10-C (Encounter, also an Ally). Spec: resources/scans/to_boldly_go/cards/encounter/2ENC06.md"""

from engine import cards as registry
from engine.cards import operation
from engine.ops import A

from ._util import count_traits

registry.ALSO_SUIT["2ENC06"] = "Ally"  # SPECIAL: This card is considered an Ally for all purposes.


@operation("2ENC06", 0, uses=[A.GAIN_SPECIALTY])
def first_words(ctx, actions):
    """PLAY: Gain 1 [Research]/[Influence]/[Military]."""
    track = yield from actions.choose("Gain 1 on which track?", [(t, t.capitalize()) for t in
                                                                 ("research", "influence", "military")])
    yield from actions.gain_specialty(track, 1)


@operation("2ENC06", 1, uses=[A.FIND, A.LOG, A.GAIN_RESOURCE], requires=lambda ctx: bool(ctx.me.locations))
def communion(ctx, actions):
    """PLAY: Select a controlled Location. For each trait and Skill icon the selected card has, find any card, except
    in your Reserve deck. Then, log the selected Location. If you have another Communication in play, gain 1 [Glory]."""
    loc = yield from actions.pick_card("Select one of your controlled Locations.", list(ctx.me.locations))
    finds = len(ctx.card(loc).traits) + len(ctx.card(loc).skills)
    for n in range(1, finds + 1):
        yield from actions.find(lambda i: True, f"any card ({n} of {finds})", exclude_reserve=True)
    yield from actions.log(loc)
    if count_traits(ctx, "Communication", exclude=ctx.this_card):
        yield from actions.gain_resource("glory", 1)
