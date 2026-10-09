"""The Picard Bot's Automated Command rows. Spec: resources/scans/base_game/command/picard.md"""

from engine.bot import row
from engine.ops import A

CREW = "picard"


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

@row(CREW, "traits", 2, uses=[A.LOG, A.GAIN_SPECIALTY, A.PROMOTE])
def synthetic_android(ctx, actions):
    """Synthetic / Android: Log the top card of the Bot deck. Gain 1 [Research]. Gain 1 [Influence]. If this card is a
    Person, promote it to Duty Officer."""
    yield from actions.log_top(1)
    yield from actions.gain_specialty("research", 1)
    yield from actions.gain_specialty("influence", 1)
    if actions.is_("Person"):
        yield from actions.promote()


@row(CREW, "traits", 3, uses=[A.DISCARD, A.SEND_AWAY_TEAM, A.ATTACK, A.REMOVE_AWAY_TEAM, A.GAIN_RESOURCE,
                             A.TAKE_INCIDENT])
def klingon(ctx, actions):
    """Klingon: Discard the top 3 cards of the Bot deck. Send an [Away Team] to a neutral Location. If able, you remove
    an [Away Team]. Otherwise, gain 1 [Glory] and take an Incident. The Away Team is one at the Location the Bot sent
    to; with none there, one of the human's choice."""
    yield from actions.discard_top(3)
    sent = yield from actions.send_away_team()
    removed = None
    if (yield from actions.attack(removes_away_teams=True)):
        human = ctx.opponent
        there = sent is not None and human is not None and sent.away.get(human.seat, 0) > 0
        removed = yield from actions.human_removes_away_team(lambda loc: not there or loc.uid == sent.uid)
    if removed is None:
        yield from actions.gain_glory(1)
        yield from actions.take_incident()


@row(CREW, "traits", 4, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.GAIN_CARD, A.LOG])
def alien(ctx, actions):
    """Alien: Discard the top card of the Bot deck. Gain 1 [Influence]. If Bot has 5+ [Influence], gain 1 [Research]
    and Cargo. Log this card."""
    yield from actions.discard_top(1)
    yield from actions.gain_specialty("influence", 1)
    if actions.track("influence") >= 5:
        yield from actions.gain_specialty("research", 1)
        yield from actions.gain_card("Cargo")
    yield from actions.log()


@row(CREW, "traits", 5, uses=[A.DISCARD, A.RETURN_INCIDENT, A.GAIN_RESOURCE, A.GAIN_SPECIALTY, A.PROMOTE])
def doctor(ctx, actions):
    """Doctor: Discard the top 2 cards of the Bot deck. If able, return an Incident from discard. Otherwise, gain 2
    [Glory] and 1 [Research]. If this card is a Person, promote it to Duty Officer."""
    yield from actions.discard_top(2)
    if not (yield from actions.return_incident_from_discard()):
        yield from actions.gain_glory(2)
        yield from actions.gain_specialty("research", 1)
    if actions.is_("Person"):
        yield from actions.promote()


@row(CREW, "traits", 6, uses=[A.SEND_AWAY_TEAM, A.PUT, A.GAIN_SPECIALTY, A.PROMOTE])
def attack(ctx, actions):
    """Attack: Send an [Away Team] to a neutral Location. If able, put a Ship from discard on top of the Bot deck.
    Otherwise, gain 1 [Influence]. If this card is a Person, promote it to Duty Officer."""
    yield from actions.send_away_team()
    if (yield from actions.put_ship_from_discard_on_top()) is None:
        yield from actions.gain_specialty("influence", 1)
    if actions.is_("Person"):
        yield from actions.promote()


# ------------------------------------------------------------------ SUITS WITH NO DUTY OFFICER

@row(CREW, "no_duty_officer", 1, uses=[A.LOG, A.GAIN_CARD, A.RETURN_INCIDENT])
def incident(ctx, actions):
    """Incident: Log the top card of the Bot deck. Gain a Person. Return this card."""
    yield from actions.log_top(1)
    yield from actions.gain_card("Person")
    yield from actions.return_incident()


@row(CREW, "no_duty_officer", 2, uses=[A.DEPLOY, A.EXPLORE, A.SEND_AWAY_TEAM])
def ship(ctx, actions):
    """Ship: Deploy this Ship; it explores. If a Person is in Bot Discard pile, send an [Away Team] to a neutral
    Location."""
    yield from actions.deploy()
    yield from actions.explore()
    if actions.in_discard("Person"):
        yield from actions.send_away_team()


@row(CREW, "no_duty_officer", 3, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM])
def ally(ctx, actions):
    """Ally: Discard the top 2 cards of the Bot deck. For each Person in Bot Discard pile, gain 1 [Influence]. For each
    Ship in Bot Discard pile, send an [Away Team] to a neutral Location."""
    yield from actions.discard_top(2)
    people = actions.count_in_discard("Person")
    if people:
        yield from actions.gain_specialty("influence", people)
    for _ in range(actions.count_in_discard("Ship")):
        yield from actions.send_away_team()


@row(CREW, "no_duty_officer", 4, uses=[A.DISCARD, A.GAIN_RESOURCE, A.GAIN_CARD, A.LOG])
def cargo(ctx, actions):
    """Cargo: Discard the top 2 cards of the Bot deck. Gain 2 [Glory]. Take a Person. Log this card."""
    yield from actions.discard_top(2)
    yield from actions.gain_glory(2)
    yield from actions.gain_card("Person", take=True)
    yield from actions.log()


@row(CREW, "no_duty_officer", 5, uses=[A.LOG, A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM, A.PROMOTE])
def person(ctx, actions):
    """Person: Log the top card of the Bot deck. Gain 1 [Research] / [Influence] (whichever is lower). Send an [Away
    Team] to a neutral Location. Promote this card to Duty Officer."""
    yield from actions.log_top(1)
    yield from actions.gain_lowest("research", "influence")
    yield from actions.send_away_team()
    yield from actions.promote()


@row(CREW, "no_duty_officer", 6, uses=[A.GAIN_CARD, A.TAKE_INCIDENT, A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM])
def directive(ctx, actions):
    """Directive: If able, gain a Klingon. Otherwise, gain a Ship / Ally and take an Incident. Gain 1 [Research] /
    [Influence] (whichever is lower). Send an [Away Team] to a neutral Location."""
    if (yield from actions.gain_card("Klingon")) is None:
        yield from actions.gain_card("Ship / Ally")
        yield from actions.take_incident()
    yield from actions.gain_lowest("research", "influence")
    yield from actions.send_away_team()


@row(CREW, "no_duty_officer", 7, uses=[A.LOG, A.GAIN_CARD])
def encounter(ctx, actions):
    """Encounter: Log the top 2 cards of the Bot deck. Take a Ship. Log this card."""
    yield from actions.log_top(2)
    yield from actions.gain_card("Ship", take=True)
    yield from actions.log()


@row(CREW, "no_duty_officer", 8, uses=[A.LOG, A.DISCARD])
def location(ctx, actions):
    """Location: Log the top card of the Bot deck. Discard the top 3 cards of the Bot deck."""
    yield from actions.log_top(1)
    yield from actions.discard_top(3)


# ------------------------------------------------------------------ SUITS WITH DUTY OFFICER

@row(CREW, "with_duty_officer", 1, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.RETURN_INCIDENT])
def incident_officer(ctx, actions):
    """Incident: Discard the top 2 cards of the Bot deck. Gain 1 [Research]. Return this card."""
    yield from actions.discard_top(2)
    yield from actions.gain_specialty("research", 1)
    yield from actions.return_incident()


@row(CREW, "with_duty_officer", 2, uses=[A.GAIN_SPECIALTY, A.DEPLOY, A.EXPLORE, A.SEND_AWAY_TEAM])
def ship_officer(ctx, actions):
    """Ship: Gain 1 [Influence]. Deploy this Ship; it explores. Send an [Away Team] to a neutral Location."""
    yield from actions.gain_specialty("influence", 1)
    yield from actions.deploy()
    yield from actions.explore()
    yield from actions.send_away_team()


@row(CREW, "with_duty_officer", 3, uses=[A.DISCARD, A.GAIN_CARD, A.LOG])
def ally_officer(ctx, actions):
    """Ally: Discard the top card of the Bot deck. Gain a Klingon > Person / Ship / Ally. Log Duty Officer. Log this
    card."""
    yield from actions.discard_top(1)
    yield from actions.gain_card("Klingon > Person / Ship / Ally")
    yield from actions.log_duty_officer()
    yield from actions.log()


@row(CREW, "with_duty_officer", 4, uses=[A.LOG, A.DISCARD, A.GAIN_CARD, A.DEPLOY, A.EXPLORE])
def cargo_officer(ctx, actions):
    """Cargo: Log the top card of the Bot deck. Discard the top 2 cards of the Bot deck. Gain a Ship. Deploy the gained
    Ship; it explores. Log Duty Officer."""
    yield from actions.log_top(1)
    yield from actions.discard_top(2)
    gained = yield from actions.gain_card("Ship")
    if gained is not None:
        yield from actions.deploy(gained)
        yield from actions.explore(gained)
    yield from actions.log_duty_officer()


@row(CREW, "with_duty_officer", 5, uses=[A.LOG, A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM])
def person_officer(ctx, actions):
    """Person: Log the top card of the Bot deck. Gain 1 [Research] / [Influence] (whichever is lower). Send an [Away
    Team] to a neutral Location."""
    yield from actions.log_top(1)
    yield from actions.gain_lowest("research", "influence")
    yield from actions.send_away_team()


@row(CREW, "with_duty_officer", 6, uses=[A.LOG, A.REMOVE_AWAY_TEAM, A.TAKE_ENCOUNTER, A.GAIN_CARD])
def directive_officer(ctx, actions):
    """Directive: If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter then log
    this card. Otherwise, gain a [Research Focus] > Alien > Cargo / Ally."""
    if not (yield from _log_location_for_encounter(actions)):
        yield from actions.gain_card("[Research Focus] > Alien > Cargo / Ally")


@row(CREW, "with_duty_officer", 7, uses=[A.GAIN_SPECIALTY, A.GAIN_CARD, A.LOG])
def encounter_officer(ctx, actions):
    """Encounter: Gain 1 [Research] / [Influence] (whichever is higher). Take a Klingon > Ally > Ship. Log this
    card."""
    yield from actions.gain_highest("research", "influence")
    yield from actions.gain_card("Klingon > Ally > Ship", take=True)
    yield from actions.log()


@row(CREW, "with_duty_officer", 8, uses=[A.LOG, A.GAIN_SPECIALTY])
def location_officer(ctx, actions):
    """Location: Log the top 2 cards of the Bot deck. Gain 1 [Research]. Log Duty Officer."""
    yield from actions.log_top(2)
    yield from actions.gain_specialty("research", 1)
    yield from actions.log_duty_officer()
