"""The Shran Bot's Automated Command rows. Spec: resources/scans/base_game/command/shran.md"""

from engine.bot import row
from engine.bot.actions import card_matches
from engine.ops import A

CREW = "shran"


def _log_location_for_encounter(actions):
    """"If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter then log this
    card." Returns True if it did."""
    if not actions.can_log_location_and_remove_two():
        return False
    yield from actions.log_controlled_location()
    yield from actions.remove_away_team(2)
    yield from actions.take_encounter()
    yield from actions.log()
    return True


# ------------------------------------------------------------------ TRAITS

@row(CREW, "traits", 2, uses=[A.JUNK, A.SEND_AWAY_TEAM, A.ATTACK, A.TAKE_INCIDENT, A.REMOVE_AWAY_TEAM])
def weapon(ctx, actions):
    """Weapon: Junk the most valuable card in the Market (ignoring any with tokens). Send an [Away Team] to a neutral
    Location. Either you take an Incident OR you remove an [Away Team]."""
    yield from actions.junk()
    yield from actions.send_away_team()
    if not (yield from actions.attack(removes_away_teams=True)):
        return
    human = ctx.opponent
    has_team = human is not None and any(loc.away.get(human.seat) for loc in [*ctx.state.neutral, *human.locations])
    options = [("incident", "Take an Incident")] + ([("team", "Remove one of your Away Teams")] if has_team else [])
    choice = options[0][0] if len(options) == 1 else (
        yield from actions.human_choice("The Bot attacks: take an Incident, or remove an Away Team?", options))
    if choice == "team":
        yield from actions.human_removes_away_team(lambda loc: True)
    else:
        yield from actions.human_takes_incident()


@row(CREW, "traits", 3, uses=[A.SEND_AWAY_TEAM, A.ATTACK, A.DISCARD, A.TAKE_INCIDENT, A.GAIN_SPECIALTY, A.PROMOTE])
def attack(ctx, actions):
    """Attack: Send an [Away Team] to a neutral Location. You discard the top card of your deck. If it is a Person,
    you take an Incident and the Bot takes an Incident. Otherwise, gain 1 [Military]. If this card is a Person,
    promote it to Duty Officer."""
    yield from actions.send_away_team()
    discarded = None
    if (yield from actions.attack()):
        discarded = yield from actions.human_discards_top()
    if discarded is not None and card_matches(discarded, "Person"):
        yield from actions.human_takes_incident()
        yield from actions.take_incident()
    else:
        yield from actions.gain_specialty("military", 1)
    if actions.is_("Person"):
        yield from actions.promote()


@row(CREW, "traits", 4, uses=[A.LOG, A.GAIN_CARD, A.RESOLVE_CARD])
def business(ctx, actions):
    """Business: Log the top card of the Bot deck. Gain a Weapon > Cargo / Ship. Resolve the top card of the Bot deck.
    Log this card."""
    yield from actions.log_top(1)
    yield from actions.gain_card("Weapon > Cargo / Ship")
    yield from actions.resolve_top()
    yield from actions.log()


@row(CREW, "traits", 5, uses=[A.DISCARD, A.GAIN_RESOURCE, A.RETURN_INCIDENT, A.PROMOTE, A.LOG])
def ambassador(ctx, actions):
    """Ambassador: Discard the top 2 cards of the Bot deck. Gain 2 [Glory]. You may return an Incident from your hand
    or discard pile. If this card is a Person, promote it to Duty Officer. Otherwise, log this card."""
    yield from actions.discard_top(2)
    yield from actions.gain_glory(2)
    yield from actions.human_may_return_incident()
    if actions.is_("Person"):
        yield from actions.promote()
    else:
        yield from actions.log()


# ------------------------------------------------------------------ SUITS WITH NO DUTY OFFICER

@row(CREW, "no_duty_officer", 1, uses=[A.GAIN_CARD, A.DISCARD, A.RETURN_INCIDENT])
def incident(ctx, actions):
    """Incident: Gain a Person. Discard the top 3 cards of the Bot deck. Return this card."""
    yield from actions.gain_card("Person")
    yield from actions.discard_top(3)
    yield from actions.return_incident()


@row(CREW, "no_duty_officer", 2, uses=[A.DEPLOY, A.EXPLORE, A.SEND_AWAY_TEAM, A.GAIN_SPECIALTY])
def ship(ctx, actions):
    """Ship: Deploy this Ship; it explores. If a Person is in Bot Discard pile, send an [Away Team] to a neutral
    Location. If a Cargo is in Bot Discard pile, gain 1 [Influence]."""
    yield from actions.deploy()
    yield from actions.explore()
    if actions.in_discard("Person"):
        yield from actions.send_away_team()
    if actions.in_discard("Cargo"):
        yield from actions.gain_specialty("influence", 1)


@row(CREW, "no_duty_officer", 3, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM])
def ally(ctx, actions):
    """Ally: Discard the top 3 cards of the Bot deck. For each Person in Bot Discard pile, gain 1 [Influence]. For each
    Ship in Bot Discard pile, send an [Away Team] to a neutral Location."""
    yield from actions.discard_top(3)
    people = actions.count_in_discard("Person")
    if people:
        yield from actions.gain_specialty("influence", people)
    for _ in range(actions.count_in_discard("Ship")):
        yield from actions.send_away_team()


@row(CREW, "no_duty_officer", 4, uses=[A.DISCARD, A.GAIN_RESOURCE, A.GAIN_CARD, A.LOG])
def cargo(ctx, actions):
    """Cargo: Discard the top 2 cards of the Bot deck. Gain 2 [Glory]. Gain a Business > Person. Log this card."""
    yield from actions.discard_top(2)
    yield from actions.gain_glory(2)
    yield from actions.gain_card("Business > Person")
    yield from actions.log()


@row(CREW, "no_duty_officer", 5, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM, A.PROMOTE])
def person(ctx, actions):
    """Person: Discard the top 2 cards of the Bot deck. Gain 1 [Influence] / [Military] (whichever is lower). Send an
    [Away Team] to a neutral Location. Promote this card to Duty Officer."""
    yield from actions.discard_top(2)
    yield from actions.gain_lowest("influence", "military")
    yield from actions.send_away_team()
    yield from actions.promote()


@row(CREW, "no_duty_officer", 6, uses=[A.GAIN_CARD, A.SEND_AWAY_TEAM, A.GAIN_RESOURCE, A.TAKE_INCIDENT])
def directive(ctx, actions):
    """Directive: Gain a Business > Cargo. Send an [Away Team] to a neutral Location. If Bot has 5+ [Influence], gain 1
    [Glory] and take an Incident."""
    yield from actions.gain_card("Business > Cargo")
    yield from actions.send_away_team()
    if actions.track("influence") >= 5:
        yield from actions.gain_glory(1)
        yield from actions.take_incident()


@row(CREW, "no_duty_officer", 7, uses=[A.DISCARD, A.GAIN_CARD, A.LOG])
def encounter(ctx, actions):
    """Encounter: Discard the top 2 cards of the Bot deck. Gain a Person. Gain a Cargo. Log this card."""
    yield from actions.discard_top(2)
    yield from actions.gain_card("Person")
    yield from actions.gain_card("Cargo")
    yield from actions.log()


@row(CREW, "no_duty_officer", 8, uses=[A.LOG, A.DISCARD])
def location(ctx, actions):
    """Location: Log the top card of the Bot deck. Discard the top 2 cards of the Bot deck."""
    yield from actions.log_top(1)
    yield from actions.discard_top(2)


# ------------------------------------------------------------------ SUITS WITH DUTY OFFICER

@row(CREW, "with_duty_officer", 1, uses=[A.LOG, A.GAIN_RESOURCE, A.RETURN_INCIDENT])
def incident_officer(ctx, actions):
    """Incident: Log the top card of the Bot deck. Gain 1 [Glory]. Return this card."""
    yield from actions.log_top(1)
    yield from actions.gain_glory(1)
    yield from actions.return_incident()


@row(CREW, "with_duty_officer", 2, uses=[A.DEPLOY, A.ENGAGE, A.SEND_AWAY_TEAM, A.GAIN_SPECIALTY])
def ship_officer(ctx, actions):
    """Ship: Deploy this Ship; it engages. Send an [Away Team] to a neutral Location. Gain 1 [Military]."""
    yield from actions.deploy()
    yield from actions.engage()
    yield from actions.send_away_team()
    yield from actions.gain_specialty("military", 1)


@row(CREW, "with_duty_officer", 3, uses=[A.GAIN_CARD, A.GAIN_SPECIALTY, A.GAIN_RESOURCE, A.LOG])
def ally_officer(ctx, actions):
    """Ally: Gain a Business > Person / Ship / Ally. If an Attack is in Bot Discard pile, gain 1 [Military] and 1
    [Glory]. Log Duty Officer. Log this card."""
    yield from actions.gain_card("Business > Person / Ship / Ally")
    if actions.in_discard("Attack"):
        yield from actions.gain_specialty("military", 1)
        yield from actions.gain_glory(1)
    yield from actions.log_duty_officer()
    yield from actions.log()


@row(CREW, "with_duty_officer", 4, uses=[A.LOG, A.GAIN_SPECIALTY])
def cargo_officer(ctx, actions):
    """Cargo: Log the top card of the Bot deck. Gain 1 [Influence]. Gain 1 [Military]. Log Duty Officer. Log this
    card."""
    yield from actions.log_top(1)
    yield from actions.gain_specialty("influence", 1)
    yield from actions.gain_specialty("military", 1)
    yield from actions.log_duty_officer()
    yield from actions.log()


@row(CREW, "with_duty_officer", 5, uses=[A.LOG, A.GAIN_SPECIALTY, A.GAIN_CARD])
def person_officer(ctx, actions):
    """Person: Log the top card of the Bot deck. Gain 1 [Influence]. Gain 1 [Military]. Take a Ship / Ally."""
    yield from actions.log_top(1)
    yield from actions.gain_specialty("influence", 1)
    yield from actions.gain_specialty("military", 1)
    yield from actions.gain_card("Ship / Ally", take=True)


@row(CREW, "with_duty_officer", 6, uses=[A.LOG, A.REMOVE_AWAY_TEAM, A.TAKE_ENCOUNTER, A.GAIN_CARD])
def directive_officer(ctx, actions):
    """Directive: If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter, then
    log this card. Otherwise, gain a Cargo / Ship."""
    if not (yield from _log_location_for_encounter(actions)):
        yield from actions.gain_card("Cargo / Ship")


@row(CREW, "with_duty_officer", 7, uses=[A.GAIN_RESOURCE, A.GAIN_SPECIALTY, A.GAIN_CARD, A.LOG])
def encounter_officer(ctx, actions):
    """Encounter: Gain 1 [Glory]. Gain 1 [Military]. Take a Ship > Ally. Log this card."""
    yield from actions.gain_glory(1)
    yield from actions.gain_specialty("military", 1)
    yield from actions.gain_card("Ship > Ally", take=True)
    yield from actions.log()


@row(CREW, "with_duty_officer", 8, uses=[A.GAIN_SPECIALTY, A.GAIN_RESOURCE, A.LOG])
def location_officer(ctx, actions):
    """Location: Gain 1 [Military]. Gain 1 [Glory]. Log Duty Officer."""
    yield from actions.gain_specialty("military", 1)
    yield from actions.gain_glory(1)
    yield from actions.log_duty_officer()
