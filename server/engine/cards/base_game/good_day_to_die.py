"""1KOL17 Good Day to Die (Directive). Spec: resources/scans/base_game/cards/captains/koloth/1KOL17.md"""

from engine.cards import operation
from engine.ops import A

from ._util import is_suit, ships


@operation("1KOL17", 0, uses=[A.LOG, A.GAIN_SPECIALTY, A.DISMISS, A.TAKE_ENCOUNTER])
def glorious_end(ctx, actions):
    """PLAY: You may log a Person beamed to a Ship to gain 1 [Military]. Log a deployed Ship and dismiss another
    deployed Ship to look at the top 2 Encounter. Take one of them and return the other to the bottom of its deck.
    Ruling: with fewer than two deployed Ships the second sentence does nothing."""
    aboard = [b for s in ships(ctx) for b in s.beamed if is_suit(b, "Person")]
    person = yield from actions.pick_card("Log a Person beamed to a Ship to gain 1 Military?", aboard, optional=True,
                                          none_label="No")
    if person:
        yield from actions.log(person)
        yield from actions.gain_specialty("military", 1)
    if len(ships(ctx)) < 2:
        return
    logged = yield from actions.pick_card("Log which deployed Ship?", ships(ctx), optional=True,
                                          none_label="Neither: keep your Ships")
    if not logged:
        return
    yield from actions.log(logged)
    dismissed = yield from actions.pick_card("Dismiss which other deployed Ship?", ships(ctx))
    yield from actions.dismiss(dismissed)
    yield from actions.take_encounter(look=2)
