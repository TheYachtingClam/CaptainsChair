"""0ENC01 Wesley Crusher (Encounter, promo). Spec: resources/scans/promo1/cards/encounter/0ENC01.md"""

from engine import cards as registry
from engine.cards import operation
from engine.ops import A

registry.ALSO_SUIT["0ENC01"] = "Person"  # SPECIAL: This card is considered a Person for all purposes; it can be promoted.
# PASSIVE: You may use the Activations and Reactions of any Person in your Staging Area.
registry.STAGING_PEOPLE_ACTIVE.add("0ENC01")


@operation("0ENC01", 0, uses=[A.ENLIST_RESERVE, A.ENLIST_DEVELOPMENT, A.DRAW, A.LOG])
def traveler(ctx, actions):
    """PLAY: Enlist a Reserve or a Development. Draw a card. Log this card."""
    options = ([("reserve", "Enlist a Reserve")] if ctx.me.reserve else []) + \
        ([("development", "Enlist a Development")] if ctx.me.development else [])
    if options:
        choice = options[0][0] if len(options) == 1 else (
            yield from actions.choose("Enlist a Reserve or a Development?", options))
        if choice == "reserve":
            yield from actions.enlist_reserve()
        else:
            yield from actions.enlist_development()
    yield from actions.draw(1)
    yield from actions.log(ctx.this_card)
