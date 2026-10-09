"""1LOC04 Ba'ku (Location). Spec: resources/scans/base_game/cards/location/1LOC04.md"""

from engine.cards import endgame, operation
from engine.ops import A, EffectCost, Spend

from ._util import beamed_here, is_suit, location_of_player


def _people_here(ctx):
    return [b for b in beamed_here(ctx) if is_suit(b, "Person")]


@operation("1LOC04", 0, uses=[A.BEAM])
def refuge(ctx, actions):
    """CONTROL: You may beam any number of Person here from your hand or Discard pile."""
    while True:
        people = [i for i in ctx.me.hand + ctx.me.discard if is_suit(i, "Person")]
        person = yield from actions.pick_card("Beam a Person here from your hand or Discard pile?", people,
                                              optional=True, none_label="Stop")
        if not person:
            break
        yield from actions.beam(person, ctx.this_card)


def _beam_officer(ctx, actions):
    officer = yield from actions.pick_card("Beam which Duty Officer here (cost)?", list(ctx.me.duty))
    yield from actions.beam(officer, ctx.this_card)


@operation("1LOC04", 1, uses=[A.BEAM, A.GAIN_ACTION],
           cost=[EffectCost(lambda ctx: bool(ctx.me.duty), _beam_officer, (A.BEAM,), "beam your Duty Officer here")])
def retire(ctx, actions):
    """ACTIVATION: Beam your Duty Officer here to gain an [Action]."""
    yield from actions.gain_action(1)


@operation("1LOC04", 2, uses=[A.RECALL], cost=[Spend(dilithium=1)], requires=lambda ctx: bool(_people_here(ctx)))
def return_to_duty(ctx, actions):
    """ACTIVATION: Spend 1 [Dilithium] to recall one Person beamed here."""
    person = yield from actions.pick_card("Recall which Person?", _people_here(ctx))
    yield from actions.recall(person)


@endgame("1LOC04")
def settlers(state, player):
    """ENDGAME: Score 1 [VP] for each Person beamed here."""
    loc = location_of_player(player, "1LOC04")
    return sum(1 for b in loc.beamed if is_suit(b, "Person")) if loc else 0
