"""3PER09 D'Erika Tendi (Person). Spec: resources/scans/second_contact/cards/person/3PER09.md"""

from engine.cards import operation
from engine.ops import A, DiscardFromHand, Spend

from ._util import count_traits, ships


@operation("3PER09", 0, uses=[A.DISCARD, A.ATTACK, A.STEAL, A.GAIN_CARD, A.GAIN_SPECIALTY, A.EXHAUST],
           cost=[DiscardFromHand(1)])
def deals(ctx, actions):
    """ATTACK PLAY: Discard a card to choose 2 of the following: steal 1 [Latinum] OR gain a Ship from the Junk OR
    gain 1 [Influence] OR gain 1 [Military]. If you have another Orion in play, you may exhaust a Ship to do up to all
    4 instead."""
    picks = 2
    ready = [s for s in ships(ctx) if not s.exhausted]
    if count_traits(ctx, "Orion", exclude=ctx.this_card) and ready and (
            yield from actions.may("Exhaust a Ship to choose up to all 4?")):
        ship = yield from actions.pick_card("Exhaust which Ship?", ready)
        yield from actions.exhaust(ship)
        picks = 4
    remaining = [("steal", "Steal 1 Latinum"), ("ship", "Gain a Ship from the Junk"),
                 ("influence", "Gain 1 Influence"), ("military", "Gain 1 Military")]
    for n in range(1, picks + 1):
        options = remaining + ([("done", "Done")] if picks == 4 and n > 2 else [])
        choice = yield from actions.choose(f"D'Erika Tendi: choose an option ({n} of {picks}).", options)
        if choice == "done":
            break
        remaining = [o for o in remaining if o[0] != choice]
        if choice == "steal":
            if (yield from actions.attack()):
                yield from actions.steal("latinum", 1)
        elif choice == "ship":
            yield from actions.gain_card(["Ship"], label="a Ship from the Junk", only_junk=True)
        else:
            yield from actions.gain_specialty(choice, 1)


@operation("3PER09", 1, uses=[A.SEND_AWAY_TEAM, A.ATTACK, A.REMOVE_AWAY_TEAM, A.GAIN_RESOURCE], cost=[Spend(latinum=2)])
def raid(ctx, actions):
    """ATTACK ACTIVATION: Spend 2 [Latinum] to send an [Away Team] to a neutral Location. You may remove an opponent
    [Away Team] from the same Location to gain 1 [Glory]."""
    loc = yield from actions.send_away_team(1, where=lambda l: l in ctx.state.neutral)
    if loc is None:
        return
    opp = ctx.opponent
    has_team = ctx.away_at(loc, opp) > 0 if opp is not None else ctx.virtual_opponent
    if has_team and (yield from actions.may("Remove an opponent Away Team there to gain 1 Glory?")):
        if (yield from actions.attack(removes_away_teams=True)):
            if opp is not None:
                yield from actions.remove_away_team(loc, opp)
            yield from actions.gain_resource("glory", 1)
