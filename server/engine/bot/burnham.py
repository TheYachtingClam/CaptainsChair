"""The Burnham Bot's Automated Command rows. Spec: resources/scans/base_game/command/burnham.md"""

from engine.bot import CLEANUP_PLACES, RESOURCE_VP, row
from engine.ops import A

CREW = "burnham"

# Special rule: during Clean-up, instead of adding [Glory], remove 1 [Glory] from the Stardate card and add 2
# [Dilithium] to one Market card (REQ-SOLO-59). At the end of the game the Bot scores 1 [VP] per [Dilithium], instead
# of 1 per 2 (REQ-SOLO-72).
CLEANUP_PLACES[CREW] = ("dilithium", 2)
RESOURCE_VP[CREW] = {"dilithium": 1}


# ------------------------------------------------------------------ TRAITS

@row(CREW, "traits", 2, uses=[A.GAIN_SPECIALTY, A.GAIN_CARD, A.DEPLOY, A.EXPLORE])
def creature(ctx, actions):
    """Creature: Gain 1 [Military]. Gain a Person / Cargo. If a Ship is in Bot Discard pile, deploy it; it explores."""
    yield from actions.gain_specialty("military", 1)
    yield from actions.gain_card("Person / Cargo")
    ship = yield from actions.deploy_from_discard()
    if ship is not None:
        yield from actions.explore(ship)


@row(CREW, "traits", 3, uses=[A.LOG, A.TAKE_INCIDENT, A.GAIN_SPECIALTY, A.GAIN_CARD])
def scientist(ctx, actions):
    """Scientist: Log the top card of the Bot deck. Take an Incident. Gain 1 [Research]. Gain an Ally."""
    yield from actions.log_top(1)
    yield from actions.take_incident()
    yield from actions.gain_specialty("research", 1)
    yield from actions.gain_card("Ally")


@row(CREW, "traits", 4, uses=[A.PROMOTE, A.DEPLOY, A.EXPLORE, A.GAIN_RESOURCE])
def anomaly(ctx, actions):
    """Anomaly: If a Person is in Bot Discard pile, promote it to Duty Officer. If this card is a Ship, deploy it; it
    explores. Otherwise, gain 2 [Glory]."""
    yield from actions.promote_from_discard()
    if actions.is_("Ship"):
        yield from actions.deploy()
        yield from actions.explore()
    else:
        yield from actions.gain_glory(2)


@row(CREW, "traits", 5, uses=[A.GAIN_CARD, A.PROMOTE])
def kelpien(ctx, actions):
    """Kelpien: If able, gain a Kelpien. Otherwise, gain the card in the Market with the most [Dilithium] > most
    [Glory]. If this card is a Person, promote it to Duty Officer."""
    if (yield from actions.gain_card("Kelpien")) is None:
        yield from actions.gain_most_dilithium()
    if actions.is_("Person"):
        yield from actions.promote()


# ------------------------------------------------------------------ SUITS WITH NO DUTY OFFICER

@row(CREW, "no_duty_officer", 1, uses=[A.DISCARD, A.GAIN_RESOURCE, A.GAIN_CARD, A.RETURN_INCIDENT])
def incident(ctx, actions):
    """Incident: Discard the top card of the Bot deck. Gain 1 [Glory]. Gain a Scientist > Creature > Person. Return
    this card."""
    yield from actions.discard_top(1)
    yield from actions.gain_glory(1)
    yield from actions.gain_card("Scientist > Creature > Person")
    yield from actions.return_incident()


@row(CREW, "no_duty_officer", 2, uses=[A.DEPLOY, A.ENGAGE, A.SEND_AWAY_TEAM])
def ship(ctx, actions):
    """Ship: Deploy this Ship; it engages. Send an [Away Team] to a neutral Location."""
    yield from actions.deploy()
    yield from actions.engage()
    yield from actions.send_away_team()


@row(CREW, "no_duty_officer", 3, uses=[A.DISCARD, A.TAKE_INCIDENT, A.GAIN_SPECIALTY])
def ally(ctx, actions):
    """Ally: Discard the top 3 cards of the Bot deck. Take an Incident. Gain 1 [Research]."""
    yield from actions.discard_top(3)
    yield from actions.take_incident()
    yield from actions.gain_specialty("research", 1)


@row(CREW, "no_duty_officer", 4, uses=[A.GAIN_CARD, A.SEND_AWAY_TEAM, A.LOG])
def cargo(ctx, actions):
    """Cargo: Gain the card in the Market with the most [Dilithium] > most [Glory]. Send an [Away Team] to a neutral
    Location. Log this card."""
    yield from actions.gain_most_dilithium()
    yield from actions.send_away_team()
    yield from actions.log()


@row(CREW, "no_duty_officer", 5, uses=[A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM, A.PROMOTE])
def person(ctx, actions):
    """Person: Gain 1 [Research]. Send an [Away Team] to a neutral Location. Promote this card to Duty Officer."""
    yield from actions.gain_specialty("research", 1)
    yield from actions.send_away_team()
    yield from actions.promote()


@row(CREW, "no_duty_officer", 6, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.REMOVE_STARDATE_GLORY])
def directive(ctx, actions):
    """Directive: Discard the top 2 cards of the Bot deck. Gain 2 [Influence]. Remove 1 [Glory] from the stardate
    card."""
    yield from actions.discard_top(2)
    yield from actions.gain_specialty("influence", 2)
    yield from actions.remove_stardate_glory(1)


@row(CREW, "no_duty_officer", 7, uses=[A.LOG, A.GAIN_CARD])
def encounter(ctx, actions):
    """Encounter: Log the top 2 cards of the Bot deck. Take a Person."""
    yield from actions.log_top(2)
    yield from actions.gain_card("Person", take=True)


@row(CREW, "no_duty_officer", 8, uses=[A.DISCARD, A.GAIN_SPECIALTY])
def location(ctx, actions):
    """Location: Discard the top 2 cards of the Bot deck. Gain 1 [Military]. Gain 1 [Research] / [Influence]
    (whichever is lower)."""
    yield from actions.discard_top(2)
    yield from actions.gain_specialty("military", 1)
    yield from actions.gain_lowest("research", "influence")


# ------------------------------------------------------------------ SUITS WITH DUTY OFFICER

@row(CREW, "with_duty_officer", 1, uses=[A.LOG, A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM, A.RETURN_INCIDENT])
def incident_officer(ctx, actions):
    """Incident: Log the top card of the Bot deck. Gain 2 [Research]. Send an [Away Team] to a neutral Location. Return
    this card."""
    yield from actions.log_top(1)
    yield from actions.gain_specialty("research", 2)
    yield from actions.send_away_team()
    yield from actions.return_incident()


@row(CREW, "with_duty_officer", 2, uses=[A.GAIN_SPECIALTY, A.DEPLOY, A.EXPLORE, A.SEND_AWAY_TEAM])
def ship_officer(ctx, actions):
    """Ship: Gain 1 [Military]. Deploy this Ship; it explores. Send an [Away Team] to a neutral Location."""
    yield from actions.gain_specialty("military", 1)
    yield from actions.deploy()
    yield from actions.explore()
    yield from actions.send_away_team()


@row(CREW, "with_duty_officer", 3, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM])
def ally_officer(ctx, actions):
    """Ally: Discard the top 3 cards of the Bot deck. Gain 1 [Military]. Send an [Away Team] to a neutral Location."""
    yield from actions.discard_top(3)
    yield from actions.gain_specialty("military", 1)
    yield from actions.send_away_team()


@row(CREW, "with_duty_officer", 4, uses=[A.LOG, A.GAIN_CARD])
def cargo_officer(ctx, actions):
    """Cargo: Log the top card of the Bot deck. Gain a Ship. Log Duty Officer."""
    yield from actions.log_top(1)
    yield from actions.gain_card("Ship")
    yield from actions.log_duty_officer()


@row(CREW, "with_duty_officer", 5, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM])
def person_officer(ctx, actions):
    """Person: Discard the top 2 cards of Bot deck. Gain 1 [Research] / [Influence] (whichever is lower). Send an [Away
    Team] to a neutral Location."""
    yield from actions.discard_top(2)
    yield from actions.gain_lowest("research", "influence")
    yield from actions.send_away_team()


@row(CREW, "with_duty_officer", 6, uses=[A.LOG, A.REMOVE_AWAY_TEAM, A.TAKE_ENCOUNTER, A.DISCARD, A.GAIN_CARD])
def directive_officer(ctx, actions):
    """Directive: If able to do both, log a controlled Location and remove an [Away Team] to gain top Encounter.
    Otherwise, discard the top 2 cards of the Bot deck and gain the card in the Market with the most [Dilithium] >
    most [Glory]. The Encounter is gained: it goes to the Bot Discard pile."""
    if ctx.me.locations and actions.away_teams_on_board() >= 1:
        yield from actions.log_controlled_location()
        yield from actions.remove_away_team(1)
        yield from actions.take_encounter(gain=True)
        return
    yield from actions.discard_top(2)
    yield from actions.gain_most_dilithium()


@row(CREW, "with_duty_officer", 7, uses=[A.GAIN_SPECIALTY, A.GAIN_CARD, A.LOG])
def encounter_officer(ctx, actions):
    """Encounter: Gain 1 [Research]. Gain 1 [Influence]. Gain a Scientist > Anomaly > Ship. Log this card."""
    yield from actions.gain_specialty("research", 1)
    yield from actions.gain_specialty("influence", 1)
    yield from actions.gain_card("Scientist > Anomaly > Ship")
    yield from actions.log()


@row(CREW, "with_duty_officer", 8, uses=[A.LOG, A.GAIN_SPECIALTY, A.DISMISS])
def location_officer(ctx, actions):
    """Location: Log the top 2 cards of the Bot deck. Gain 1 [Research]. Dismiss Duty Officer."""
    yield from actions.log_top(2)
    yield from actions.gain_specialty("research", 1)
    yield from actions.dismiss_duty_officer()
