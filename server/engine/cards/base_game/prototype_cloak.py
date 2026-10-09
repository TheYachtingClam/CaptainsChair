"""1KOL03 Prototype Cloak (Cargo, Development). Spec: resources/scans/base_game/cards/captains/koloth/1KOL03.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

from ._util import has_trait, is_suit, opponent_ships, others_in_hand, ships

development_cost("1KOL03", Spend(dilithium=3))


@operation("1KOL03", 0, uses=[A.DEPLOY, A.REFRESH, A.JUNK, A.ATTACK, A.FORCE, A.DISMISS, A.TAKE_INCIDENT])
def field_test(ctx, actions):
    """ATTACK PLAY: Deploy this card. Refresh a Ship. Junk a card from the Market. If the opponent has 2 or more Ship
    deployed, force them to either: dismiss one OR take an Incident. The Cadet virtual opponent has no Ships."""
    yield from actions.deploy(ctx.this_card)
    ship = yield from actions.pick_card("Refresh which Ship?", [s for s in ships(ctx) if s.exhausted])
    if ship:
        yield from actions.refresh(ship)
    yield from actions.junk()
    opp = ctx.opponent
    if opp is None or len(opponent_ships(ctx)) < 2 or not (yield from actions.attack()):
        return
    choice = yield from actions.choose("Prototype Cloak: dismiss one of your Ships, or take an Incident?",
                                       [("dismiss", "Dismiss a Ship"), ("incident", "Take an Incident")], opp.seat)
    if choice == "dismiss":
        theirs = yield from actions.pick_card("Dismiss which Ship?", opponent_ships(ctx), seat=opp.seat)
        yield from actions.dismiss(theirs)
    else:
        yield from actions.take_incident(opponent=True)


@operation("1KOL03", 1, uses=[A.TREAT_AS, A.DISCARD, A.SEND_AWAY_TEAM],
           trigger=lambda ctx, ev: ev["kind"] == "deploy" and ev["seat"] == ctx.me.seat
           and ctx.event_card is not None and is_suit(ctx.event_card, "Ship") and not has_trait(ctx.event_card, "Cloak"))
def cloak_ship(ctx, actions):
    """REACTION: After deploying a Ship without Cloak, that Ship gains Cloak for the remainder of your turn. Then, you
    may discard a card to send an [Away Team] to a Location, ignoring any opponent Ship."""
    yield from actions.treat_as(ctx.event_card, "Cloak")
    if others_in_hand(ctx) and (yield from actions.may("Discard a card to send an Away Team, ignoring opponent Ships?")):
        yield from actions.discard(1)
        yield from actions.send_away_team(1, ignore_ships=True)
