"""The Riker Bot's Automated Command rows. Spec: resources/scans/second_contact/command/riker.md"""

from engine.bot import VALUE_BONUS, row
from engine.bot.georgiou import _directive_with_officer
from engine.ops import A, card

CREW = "riker"
FAVOURITES = {"NX-01", "Android", "Pakled", "Lower Decker", "Beverage", "Betazoid"}

# Special rule: cards with any of NX-01, Android, Pakled, Lower Decker, Beverage or Betazoid are +1 value for the Bot.
VALUE_BONUS[CREW] = lambda inst: 1 if FAVOURITES & set(card(inst).traits) else 0


# ------------------------------------------------------------------ TRAITS

@row(CREW, "traits", 2, uses=[A.GAIN_RESOURCE, A.LOG])
def nx01_android_pakled(ctx, actions):
    """NX-01 / Android / Pakled: Gain 3 [Glory]. Log this card."""
    yield from actions.gain_glory(3)
    yield from actions.log()


@row(CREW, "traits", 3, uses=[A.GAIN_CARD, A.RESOLVE_CARD, A.GAIN_SPECIALTY, A.TAKE_INCIDENT, A.LOG])
def lower_decker(ctx, actions):
    """Lower Decker: Gain a Beverage > Cargo. Resolve a Person from the Discard pile, if able; otherwise gain 1
    [Research], take an Incident, and resolve the top card of the Supplement deck, then log this card."""
    yield from actions.gain_card("Beverage > Cargo")
    if (yield from actions.resolve_from_discard("Person")) is None:
        yield from actions.gain_specialty("research", 1)
        yield from actions.take_incident()
        yield from actions.resolve_supplement_top()
        yield from actions.log()


@row(CREW, "traits", 4, uses=[A.GAIN_SPECIALTY, A.DISCARD, A.RETURN_INCIDENT, A.SEND_AWAY_TEAM])
def betazoid(ctx, actions):
    """Betazoid: Gain 1 [Influence]. Discard the top card of the Bot deck. Return an Incident from the Bot Discard
    pile, if able; otherwise send an [Away Team] to a neutral Location."""
    yield from actions.gain_specialty("influence", 1)
    yield from actions.discard_top(1)
    if not (yield from actions.return_incident_from_discard()):
        yield from actions.send_away_team()


@row(CREW, "traits", 5, uses=[A.GAIN_RESOURCE, A.GAIN_CARD, A.LOG, A.CONTINUE_RESOLUTION])
def beverage(ctx, actions):
    """Beverage: Gain 1 [Glory], take an Ally and log the Duty Officer. Continue resolution."""
    yield from actions.gain_glory(1)
    yield from actions.gain_card("Ally", take=True)
    yield from actions.log_duty_officer()
    yield from actions.continue_resolution()


@row(CREW, "traits", 6, uses=[A.GAIN_RESOURCE, A.ATTACK, A.DISMISS, A.TAKE_INCIDENT, A.CONTINUE_RESOLUTION])
def attack(ctx, actions):
    """Attack: Gain 1 [Glory]. If you have at least 1 Ship at a neutral Location, you either dismiss one of them OR
    take an Incident. Continue resolution."""
    yield from actions.gain_glory(1)
    human = actions.human
    neutral = {loc.uid for loc in ctx.state.neutral}
    if human is not None and any(s.at in neutral for s in human.fleet):
        if (yield from actions.attack()):
            yield from actions.human_dismisses_ship_or_takes_incident()
    yield from actions.continue_resolution()


# ------------------------------------------------------------------ SUITS WITH NO DUTY OFFICER

@row(CREW, "no_duty_officer", 1, uses=[A.GAIN_CARD, A.LOG, A.GAIN_SPECIALTY, A.RETURN_INCIDENT])
def incident(ctx, actions):
    """Incident: Gain a Person. Log the top card of the Bot deck. Gain 1 [Research] / [Military] (whichever is lower).
    Return this card."""
    yield from actions.gain_card("Person")
    yield from actions.log_top(1)
    yield from actions.gain_lowest("research", "military")
    yield from actions.return_incident()


@row(CREW, "no_duty_officer", 2, uses=[A.DEPLOY, A.ENGAGE, A.DISCARD, A.SEND_AWAY_TEAM])
def ship(ctx, actions):
    """Ship: Deploy this Ship; it engages. Discard the top card of the Bot deck. If there is a Starfleet in the Bot
    discard pile, send an [Away Team] to a neutral Location."""
    yield from actions.deploy()
    yield from actions.engage()
    yield from actions.discard_top(1)
    if actions.in_discard("Starfleet"):
        yield from actions.send_away_team()


@row(CREW, "no_duty_officer", 3, uses=[A.TAKE_INCIDENT, A.GAIN_CARD, A.GAIN_SPECIALTY, A.LOG])
def ally(ctx, actions):
    """Ally: Take an Incident and a Person. Gain 2 [Research] / [Influence] / [Military] (whichever is lower). Log this
    card."""
    yield from actions.take_incident()
    yield from actions.gain_card("Person", take=True)
    yield from actions.gain_lowest(n=2)
    yield from actions.log()


@row(CREW, "no_duty_officer", 4, uses=[A.JUNK, A.GAIN_RESOURCE, A.RESOLVE_CARD, A.LOG])
def cargo(ctx, actions):
    """Cargo: Junk the most valuable card in the Market (ignoring any with tokens). Gain 1 [Glory]. Resolve a Person /
    Ally from the Discard pile, if able. Log this card."""
    yield from actions.junk()
    yield from actions.gain_glory(1)
    yield from actions.resolve_from_discard("Person / Ally")
    yield from actions.log()


@row(CREW, "no_duty_officer", 5, uses=[A.DISCARD, A.RETURN_INCIDENT, A.GAIN_CARD, A.PROMOTE])
def person(ctx, actions):
    """Person: Discard the top 3 cards of the Bot deck. If one of the discarded cards is Incident, return it; otherwise
    gain a Cargo. Promote this card to Duty Officer."""
    discarded = yield from actions.discard_top(3)
    incident_card = next((i for i in discarded if card(i).suit == "Incident"), None)
    if incident_card is not None:
        yield from actions.return_incident(incident_card)
    else:
        yield from actions.gain_card("Cargo")
    yield from actions.promote()


@row(CREW, "no_duty_officer", 6, uses=[A.GAIN_SPECIALTY, A.TAKE_INCIDENT, A.GAIN_CARD, A.SEND_AWAY_TEAM])
def directive(ctx, actions):
    """Directive: Gain 1 [Research]. If this card has a Skill icon, gain 2 (additional) [Research]; otherwise take an
    Incident and a Ship / Ally / Person. Send an [Away Team] to a neutral Location."""
    yield from actions.gain_specialty("research", 1)
    if actions.has_skill_icon():
        yield from actions.gain_specialty("research", 2)
    else:
        yield from actions.take_incident()
        yield from actions.gain_card("Ship / Ally / Person", take=True)
    yield from actions.send_away_team()


@row(CREW, "no_duty_officer", 7, uses=[A.DISCARD, A.GAIN_RESOURCE, A.LOG])
def encounter(ctx, actions):
    """Encounter: Discard the entire Bot deck. Gain 2 [Glory]. Log this card."""
    yield from actions.discard_deck()
    yield from actions.gain_glory(2)
    yield from actions.log()


@row(CREW, "no_duty_officer", 8, uses=[A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM])
def location(ctx, actions):
    """Location: Gain 1 [Influence]. Send an [Away Team] to a neutral Location."""
    yield from actions.gain_specialty("influence", 1)
    yield from actions.send_away_team()


# ------------------------------------------------------------------ SUITS WITH DUTY OFFICER

@row(CREW, "with_duty_officer", 1, uses=[A.GAIN_CARD, A.GAIN_SPECIALTY, A.RETURN_INCIDENT])
def incident_officer(ctx, actions):
    """Incident: Take a [Research Focus]/[Military Focus], if able. Gain 1 [Research] / [Military] (whichever is
    higher). Return this card."""
    yield from actions.gain_card("[Research Focus] / [Military Focus]", take=True)
    yield from actions.gain_highest("research", "military")
    yield from actions.return_incident()


@row(CREW, "with_duty_officer", 2, uses=[A.DEPLOY, A.ENGAGE, A.SEND_AWAY_TEAM, A.RESOLVE_CARD, A.DISMISS])
def ship_officer(ctx, actions):
    """Ship: Deploy this Ship; it engages. Send an [Away Team] to a neutral Location. If this card is Starfleet,
    resolve a Directive from the Bot Discard pile. Dismiss Duty Officer."""
    yield from actions.deploy()
    yield from actions.engage()
    yield from actions.send_away_team()
    if "Starfleet" in card(actions.this).traits:
        yield from actions.resolve_from_discard("Directive")
    yield from actions.dismiss_duty_officer()


@row(CREW, "with_duty_officer", 3, uses=[A.GAIN_SPECIALTY, A.GAIN_CARD, A.DISMISS, A.LOG])
def ally_officer(ctx, actions):
    """Ally: Gain 2 [Influence]. If able to do both, gain [Research Focus]/[Influence Focus]/[Military Focus] and
    dismiss the Duty Officer. Otherwise log the top card of the Bot deck. Log this card."""
    from engine.bot import market_cards
    from engine.bot.actions import card_matches

    yield from actions.gain_specialty("influence", 2)
    focus = "[Research Focus] / [Influence Focus] / [Military Focus]"
    able = actions.duty_officer is not None and any(
        card_matches(i, term) for i in market_cards(ctx.state) for term in focus.split(" / "))
    if able:
        yield from actions.gain_card(focus)
        yield from actions.dismiss_duty_officer()
    else:
        yield from actions.log_top(1)
    yield from actions.log()


@row(CREW, "with_duty_officer", 4, uses=[A.JUNK, A.DISCARD, A.RETURN_INCIDENT, A.GAIN_RESOURCE])
def cargo_officer(ctx, actions):
    """Cargo: Junk the most valuable card in the Market (ignoring any with tokens). Discard the top 2 cards of the Bot
    deck. Return an Incident from the Bot Discard pile, if able. Gain 1 [Glory]."""
    yield from actions.junk()
    yield from actions.discard_top(2)
    yield from actions.return_incident_from_discard()
    yield from actions.gain_glory(1)


@row(CREW, "with_duty_officer", 5, uses=[A.TAKE_INCIDENT, A.RESOLVE_CARD, A.GAIN_CARD, A.DISMISS])
def person_officer(ctx, actions):
    """Person: Take an Incident. Resolve a Ship from the Bot Discard pile if able; otherwise take a Ship and dismiss
    Duty Officer."""
    yield from actions.take_incident()
    if (yield from actions.resolve_from_discard("Ship")) is None:
        yield from actions.gain_card("Ship", take=True)
        yield from actions.dismiss_duty_officer()


@row(CREW, "with_duty_officer", 6, uses=[A.LOG, A.REMOVE_AWAY_TEAM, A.TAKE_ENCOUNTER, A.GAIN_SPECIALTY, A.DISCARD])
def directive_officer(ctx, actions):
    """Directive: If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter, then
    log this card. Otherwise, gain 1 [Research] / [Military] (whichever is lower), and discard the top 2 cards of the
    Bot deck."""
    if not (yield from _directive_with_officer(actions)):
        yield from actions.gain_lowest("research", "military")
        yield from actions.discard_top(2)


@row(CREW, "with_duty_officer", 7, uses=[A.GAIN_RESOURCE, A.DISCARD, A.RESOLVE_CARD, A.RETURN_INCIDENT, A.LOG])
def encounter_officer(ctx, actions):
    """Encounter: Gain 1 [Glory]. Discard the entire Bot deck. Resolve the top card of the Supplement deck. Return an
    Incident from the Bot Discard pile, if able. Log this card."""
    yield from actions.gain_glory(1)
    yield from actions.discard_deck()
    yield from actions.resolve_supplement_top()
    yield from actions.return_incident_from_discard()
    yield from actions.log()


@row(CREW, "with_duty_officer", 8, uses=[A.GAIN_SPECIALTY, A.DISCARD, A.LOG])
def location_officer(ctx, actions):
    """Location: Gain 1 [Influence]. Discard the top card of the Supplement deck. Log the Duty Officer."""
    yield from actions.gain_specialty("influence", 1)
    yield from actions.discard_supplement_top()
    yield from actions.log_duty_officer()
