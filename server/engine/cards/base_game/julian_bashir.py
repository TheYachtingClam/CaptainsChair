"""1SIS08 Julian Bashir (Person, Development). Spec: resources/scans/base_game/cards/captains/sisko/1SIS08.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import has_trait, incidents_in_hand, is_suit

development_cost("1SIS08", Spend(dilithium=2))
OBRIEN = "1SIS13"


@operation("1SIS08", 0, uses=[A.FREE_PLAY, A.GAIN_SPECIALTY])
def frontier_medicine(ctx, actions):
    """PLAY: Free play an Incident from your hand or Discard pile. If you do, gain 1 [Research]."""
    incidents = actions.free_play_candidates(lambda i: is_suit(i, "Incident"), ("hand", "discard"))
    incident = yield from actions.pick_card("Free play which Incident?", incidents)
    if incident:
        yield from actions.free_play(incident)
        yield from actions.gain_specialty("research", 1)


@operation("1SIS08", 1, uses=[A.FIND, A.RETURN_INCIDENT], cost=[Spend(dilithium=1)])
def section_31(ctx, actions):
    """ACTIVATION: Spend 1 [Dilithium] to choose 2 of the following: find a Person with Spy OR find a Person with
    Augment OR find Miles O'Brien OR return an Incident."""
    labels = {"spy": "Find a Person with Spy", "augment": "Find a Person with Augment",
              "obrien": "Find Miles O'Brien", "incident": "Return an Incident"}
    for n in (1, 2):
        able = {k: True for k in labels}
        able["incident"] = bool(incidents_in_hand(ctx))
        choices = [(k, v) for k, v in labels.items() if able[k]]
        if not choices:
            return
        pick = yield from actions.choose(f"Choose option {n} of 2.", choices)
        del labels[pick]
        if pick == "spy":
            yield from actions.find(lambda i: is_suit(i, "Person") and has_trait(i, "Spy"), "a Person with Spy")
        elif pick == "augment":
            yield from actions.find(lambda i: is_suit(i, "Person") and has_trait(i, "Augment"), "a Person with Augment")
        elif pick == "obrien":
            yield from actions.find(lambda i: i.card == OBRIEN, "Miles O'Brien")
        else:
            incident = yield from actions.pick_card("Return which Incident?", incidents_in_hand(ctx))
            if incident:
                yield from actions.return_incident(incident)
