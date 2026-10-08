"""1PER07 Captain Dorg (Person). Spec: resources/scans/base_game/cards/person/1PER07.md"""

from engine.cards import operation
from engine.ops import A, EffectCost

from ._util import has_trait, others_in_hand


@operation("1PER07", 0, uses=[A.DISCARD, A.GAIN_CARD, A.GAIN_RESOURCE], requires=lambda ctx: bool(others_in_hand(ctx)))
def plunder(ctx, actions):
    """PLAY: Discard a card. If the discarded card is a Weapon, gain a Ship. If it has [Influence]/[Influence
    Focus]/[Military]/[Military Focus], gain 2 [Glory]."""
    discarded = yield from actions.discard(1)
    if not discarded:
        return
    card = discarded[0]
    if has_trait(card, "Weapon"):
        yield from actions.gain_card(["Ship"], label="a Ship")
    if ctx.has_specialty_icon(card, "influence") or ctx.has_specialty_icon(card, "military"):
        yield from actions.gain_resource("glory", 2)


def _klingons(ctx):
    """Your Klingons that can be dismissed: on the table or beamed, this card included."""
    return [i for i in ctx.in_play() if i not in ctx.me.staging and ctx.has(i, "Klingon")]


def _dismiss_a_klingon(ctx, actions):
    klingon = yield from actions.pick_card("Dismiss which Klingon (cost)?", _klingons(ctx))
    yield from actions.dismiss(klingon)


@operation("1PER07", 1, uses=[A.DISMISS, A.GAIN_ACTION],
           cost=[EffectCost(lambda ctx: bool(_klingons(ctx)), _dismiss_a_klingon, (A.DISMISS,), "dismiss a Klingon")],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and ctx.has(ctx.event_card, "Shady"))
def mutiny(ctx, actions):
    """REACTION: After putting a Shady into play, dismiss a Klingon (can be this card) to gain an [Action]."""
    yield from actions.gain_action(1)


@operation("1PER07", 2, uses=[A.ATTACK, A.REMOVE_AWAY_TEAM, A.GAIN_RESOURCE],
           trigger=lambda ctx, ev: ev["kind"] == "put_into_play" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and (ctx.has(ctx.event_card, "Klingon") or ctx.has(ctx.event_card, "Pakled")))
def raid(ctx, actions):
    """ATTACK REACTION: After putting a Klingon/Pakled into play, remove up to 2 opponent [Away Team] from the same
    Location. Gain 1 [Glory] for each [Away Team] removed this way.
    Cadet: the virtual opponent has 1 Away Team at each neutral Location, so 1 is removed (REQ-CTM-12)."""
    opp = ctx.opponent
    targets = [loc for loc in ctx.all_locations() if ctx.away_at(loc, opp) > 0] if opp is not None \
        else list(ctx.state.neutral)
    if not targets or not (yield from actions.attack(removes_away_teams=True)):
        return
    loc = yield from actions.pick_card("Remove opponent Away Teams from which Location?", targets)
    if opp is None:
        yield from actions.gain_resource("glory", 1)
        return
    removed = 0
    for _ in range(min(2, ctx.away_at(loc, opp))):
        if removed and not (yield from actions.may("Remove a second Away Team there?")):
            break
        yield from actions.remove_away_team(loc, opp)
        removed += 1
    yield from actions.gain_resource("glory", removed)
