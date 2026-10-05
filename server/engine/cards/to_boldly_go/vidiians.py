"""2ALL16 Vidiians (Ally). Spec: resources/scans/to_boldly_go/cards/ally/2ALL16.md"""

from engine.cards import operation
from engine.ops import A

from ._util import is_suit


@operation("2ALL16", 0, uses=[A.FIND, A.LOG, A.FREE_PLAY, A.GAIN_RESOURCE])
def harvest(ctx, actions):
    """PLAY: You may find and log a Person. You may find and free play an Incident. If you did both, gain 1
    [Glory]. Otherwise, log this card."""
    logged = played = False
    if (yield from actions.may("Find a Person and log it?")):
        person, _ = yield from actions.find(lambda i: is_suit(i, "Person"), "a Person", optional=True)
        if person:
            yield from actions.log(person)
            logged = True
    if (yield from actions.may("Find an Incident and free play it?")):
        incident, _ = yield from actions.find(lambda i: is_suit(i, "Incident"), "an Incident", optional=True)
        if incident and actions.free_play_candidates(lambda i: i is incident):
            yield from actions.free_play(incident)
            played = True
    if logged and played:
        yield from actions.gain_resource("glory", 1)
    else:
        yield from actions.log(ctx.this_card)
