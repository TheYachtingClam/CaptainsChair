"""3RIK12 Tactical Officer (U.S.S. Titan) (Person). Spec: resources/scans/second_contact/cards/captains/william riker/3RIK12.md"""

from engine.cards import operation, skill_icons
from engine.ops import A, card

from ._util import ctx_for, has_trait, is_suit, ships


@operation("3RIK12", 0, uses=[A.SEND_AWAY_TEAM, A.BEAM, A.PROMOTE])
def tactical(ctx, actions):
    """PLAY: Send an [Away Team] to a Location. You may beam a card from your hand or Staging Area to a deployed Ship.
    If you have another Starfleet in your Staging Area, you may promote this card to Duty Officer."""
    yield from actions.send_away_team(1)
    cards = [i for i in ctx.me.hand + ctx.me.staging if i is not ctx.this_card]
    if ships(ctx):
        item = yield from actions.pick_card("Beam a card to a Ship?", cards, optional=True, none_label="No")
        if item:
            ship = yield from actions.pick_card("To which Ship?", ships(ctx))
            yield from actions.beam(item, ship)
    me = ctx.this_card
    if me in ctx.me.staging and any(i is not me and has_trait(i, "Starfleet") for i in ctx.me.staging) and (
            yield from actions.may("Promote the Tactical Officer to Duty Officer?")):
        yield from actions.promote(me)


@skill_icons("3RIK12")
def crew_strength(state, owner, inst):
    """PASSIVE: This card has 1 [Military] for each Person with Starfleet you have in play (max 3), excluding this
    card."""
    n = sum(1 for i in ctx_for(state, owner).in_play()
            if i is not inst and is_suit(i, "Person") and "Starfleet" in card(i).traits)
    return ["Military"] * min(3, n)
