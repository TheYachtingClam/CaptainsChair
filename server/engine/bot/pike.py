"""The Pike Bot's Automated Command rows. Spec: resources/scans/second_contact/command/pike.md"""

from engine.bot import ON_RESOLVE, row
from engine.bot.georgiou import _directive_with_officer
from engine.ops import A, card

CREW = "pike"
SKILL_TRACKS = {"Research": "research", "Influence": "influence", "Military": "military"}


def _skills_special_rule(ctx, actions):
    """Special rule: when a card with one or more [Research]/[Influence]/[Military] Skill icons is resolved, the Bot
    gains 1 on the matching track; with several different Skills (or an [Any Skill]), whichever track is higher."""
    skills = card(actions.this).skills
    tracks = list(SKILL_TRACKS.values()) if "Any" in skills else [SKILL_TRACKS[s] for s in skills if s in SKILL_TRACKS]
    if tracks:
        yield from actions.gain_highest(*dict.fromkeys(tracks))


ON_RESOLVE[CREW] = (_skills_special_rule, (A.GAIN_SPECIALTY,))


def _has(inst, trait):
    return trait in card(inst).traits


# ------------------------------------------------------------------ TRAITS

@row(CREW, "traits", 2, uses=[A.DISCARD, A.TAKE_INCIDENT, A.GAIN_CARD, A.PROMOTE, A.RESOLVE_CARD, A.LOG,
                             A.GAIN_RESOURCE])
def time_travel(ctx, actions):
    """Time Travel: If this card is a Person, discard the top card of the Bot deck, take an Incident, gain a Person /
    Ship, and promote this card to Duty Officer. Otherwise, if this card is a Cargo, gain an Incident and resolve the
    top card of the Supplement deck, then log that card. Otherwise, gain 3 [Glory] and log this card."""
    if actions.is_("Person"):
        yield from actions.discard_top(1)
        yield from actions.take_incident()
        yield from actions.gain_card("Person / Ship")
        yield from actions.promote()
    elif actions.is_("Cargo"):
        yield from actions.gain_incident()
        resolved = yield from actions.resolve_supplement_top()
        if resolved is not None:
            yield from actions.log(resolved)
    else:
        yield from actions.gain_glory(3)
        yield from actions.log()


@row(CREW, "traits", 3, uses=[A.DISCARD, A.SEND_AWAY_TEAM, A.RESOLVE_CARD, A.CONTINUE_RESOLUTION])
def engineer(ctx, actions):
    """Engineer: Discard the top 2 cards of the Bot deck. Send an [Away Team] to a neutral Location. Resolve a Cargo /
    Ship from the Bot Discard if able; otherwise continue resolution."""
    yield from actions.discard_top(2)
    yield from actions.send_away_team()
    if (yield from actions.resolve_from_discard("Cargo / Ship")) is None:
        yield from actions.continue_resolution()


@row(CREW, "traits", 4, uses=[A.RETURN_INCIDENT, A.SEND_AWAY_TEAM, A.GAIN_CARD, A.GAIN_SPECIALTY,
                             A.CONTINUE_RESOLUTION])
def doctor(ctx, actions):
    """Doctor: If able, return an Incident from the Bot Discard; otherwise (if able) send an [Away Team] to a Location
    where the Bot has a Ship. If Bot has 6 or more [Research], gain a Time Travel > Doctor > Person. Otherwise, gain 1
    [Research] and continue resolution."""
    if not (yield from actions.return_incident_from_discard()):
        yield from actions.send_away_team(where=lambda loc: bool(ctx.ships_at(loc)))
    if actions.track("research") >= 6:
        yield from actions.gain_card("Time Travel > Doctor > Person")
    else:
        yield from actions.gain_specialty("research", 1)
        yield from actions.continue_resolution()


@row(CREW, "traits", 5, uses=[A.DISCARD])
def telepath(ctx, actions):
    """Telepath: Discard the top 3 cards of the Bot deck. Discard the top card of the Supplement deck."""
    yield from actions.discard_top(3)
    yield from actions.discard_supplement_top()


@row(CREW, "traits", 6, uses=[A.TAKE_INCIDENT, A.LOG])
def attack_shady(ctx, actions):
    """Attack / Shady: Gain an Incident. Log this card."""
    yield from actions.gain_incident()
    yield from actions.log()


# ------------------------------------------------------------------ SUITS WITH NO DUTY OFFICER

@row(CREW, "no_duty_officer", 1, uses=[A.GAIN_CARD, A.GAIN_SPECIALTY, A.RETURN_INCIDENT])
def incident(ctx, actions):
    """Incident: If able, gain [Research Focus]/[Influence Focus]; otherwise gain 1 [Research] / [Influence] /
    [Military] (whichever is lower). Return this card."""
    if (yield from actions.gain_card("[Research Focus] / [Influence Focus]")) is None:
        yield from actions.gain_lowest()
    yield from actions.return_incident()


@row(CREW, "no_duty_officer", 2, uses=[A.DISCARD, A.DEPLOY, A.EXPLORE, A.SEND_AWAY_TEAM])
def ship(ctx, actions):
    """Ship: Discard the top 3 cards of the Bot deck. Deploy this Ship; it explores. If a Person is in the Bot Discard
    pile, send an [Away Team] to a neutral Location."""
    yield from actions.discard_top(3)
    yield from actions.deploy()
    yield from actions.explore()
    if actions.in_discard("Person"):
        yield from actions.send_away_team()


@row(CREW, "no_duty_officer", 3, uses=[A.DISCARD, A.GAIN_CARD, A.GAIN_SPECIALTY, A.LOG])
def ally(ctx, actions):
    """Ally: Discard the top 2 cards of the Bot deck. Gain a Person. Gain 1 [Research] / [Influence] / [Military]
    (whichever is lower). Log this card."""
    yield from actions.discard_top(2)
    yield from actions.gain_card("Person")
    yield from actions.gain_lowest()
    yield from actions.log()


@row(CREW, "no_duty_officer", 4, uses=[A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM, A.DISCARD, A.LOG, A.GAIN_RESOURCE])
def cargo(ctx, actions):
    """Cargo: Gain 1 [Influence]. Send an [Away Team] to a neutral Location. Discard the top 2 cards of the Bot deck.
    Log a non-Time Travel Person from the Bot Discard (if able) to gain 1 [Glory]. Log this card."""
    yield from actions.gain_specialty("influence", 1)
    yield from actions.send_away_team()
    yield from actions.discard_top(2)
    logged = yield from actions.log_from_discard(lambda i: card(i).suit == "Person" and not _has(i, "Time Travel"))
    if logged is not None:
        yield from actions.gain_glory(1)
    yield from actions.log()


@row(CREW, "no_duty_officer", 5, uses=[A.GAIN_CARD, A.SEND_AWAY_TEAM, A.PROMOTE])
def person(ctx, actions):
    """Person: If there is no Starfleet in the Bot Discard, take a [Research Focus]/[Influence Focus] > Starfleet /
    Augment > Ship; otherwise send an [Away Team] to a neutral Location. Promote this card to Duty Officer."""
    if not actions.in_discard("Starfleet"):
        yield from actions.gain_card("[Research Focus] / [Influence Focus] > Starfleet / Augment > Ship", take=True)
    else:
        yield from actions.send_away_team()
    yield from actions.promote()


@row(CREW, "no_duty_officer", 6, uses=[A.DISCARD, A.RESOLVE_CARD, A.TAKE_INCIDENT, A.SEND_AWAY_TEAM])
def directive(ctx, actions):
    """Directive: Discard the top 2 cards of the Bot deck. Resolve a Ship from the Bot Discard, if able; otherwise
    take an Incident and send an [Away Team] to a neutral Location."""
    yield from actions.discard_top(2)
    if (yield from actions.resolve_from_discard("Ship")) is None:
        yield from actions.take_incident()
        yield from actions.send_away_team()


@row(CREW, "no_duty_officer", 7, uses=[A.DISCARD, A.GAIN_CARD, A.LOG])
def encounter(ctx, actions):
    """Encounter: Discard the top 3 cards of the Bot deck. Take a Time Travel > Doctor > [Research Focus]/[Influence
    Focus]/[Military Focus] > Person. Discard the top card of the Supplement deck. Log this card."""
    yield from actions.discard_top(3)
    yield from actions.gain_card("Time Travel > Doctor > [Research Focus] / [Influence Focus] / [Military Focus] > "
                                 "Person", take=True)
    yield from actions.discard_supplement_top()
    yield from actions.log()


@row(CREW, "no_duty_officer", 8, uses=[A.DISCARD, A.GAIN_RESOURCE, A.SEND_AWAY_TEAM])
def location(ctx, actions):
    """Location: Discard the top 2 cards of the Bot deck. Gain 1 [Glory]. If this card is a Starbase, send an [Away
    Team] to a neutral Location."""
    yield from actions.discard_top(2)
    yield from actions.gain_glory(1)
    if _has(actions.this, "Starbase"):
        yield from actions.send_away_team()


# ------------------------------------------------------------------ SUITS WITH DUTY OFFICER

@row(CREW, "with_duty_officer", 1, uses=[A.DISCARD, A.GAIN_CARD, A.GAIN_SPECIALTY, A.RETURN_INCIDENT])
def incident_officer(ctx, actions):
    """Incident: Discard the top card of the Bot deck. If Bot has 10 or more [Research]/[Influence]/[Military] and if
    able, gain a card with matching Focus, including from the Junk; otherwise gain 1 [Research] and 1 [Influence].
    Return this card."""
    yield from actions.discard_top(1)
    high = [t for t in ("research", "influence", "military") if actions.track(t) >= 10]
    gained = None
    if high:
        wanted = " / ".join(f"[{t.capitalize()} Focus]" for t in high)
        gained = yield from actions.gain_card(wanted, including_junk=True)
    if gained is None:
        yield from actions.gain_specialty("research", 1)
        yield from actions.gain_specialty("influence", 1)
    yield from actions.return_incident()


@row(CREW, "with_duty_officer", 2, uses=[A.DISCARD, A.DEPLOY, A.ENGAGE, A.SEND_AWAY_TEAM])
def ship_officer(ctx, actions):
    """Ship: For each Starbase and Engineer in play, discard the top card of the Bot deck. Deploy this Ship; it
    engages. Send an [Away Team] to a neutral Location. ("In play" is read as the Bot's cards.)"""
    count = sum(_has(i, "Starbase") + _has(i, "Engineer") for i in actions.bot_in_play() if i is not actions.this)
    if count:
        yield from actions.discard_top(count)
    yield from actions.deploy()
    yield from actions.engage()
    yield from actions.send_away_team()


@row(CREW, "with_duty_officer", 3, uses=[A.GAIN_SPECIALTY, A.GAIN_CARD, A.GAIN_RESOURCE, A.LOG, A.DISMISS])
def ally_officer(ctx, actions):
    """Ally: Gain 1 [Influence] / [Military] (whichever is lower). If Bot has 8 or fewer [Research], gain a Ship from
    the top of the deck and gain 1 [Research]; otherwise take Time Travel > Doctor > Person, and gain 1 [Glory] for
    each Doctor in play or in the Bot Discard. Log this card and dismiss Duty Officer."""
    yield from actions.gain_lowest("influence", "military")
    if actions.track("research") <= 8:
        yield from actions.gain_top_of_deck("Ship")
        yield from actions.gain_specialty("research", 1)
    else:
        yield from actions.gain_card("Time Travel > Doctor > Person", take=True)
        doctors = sum(_has(i, "Doctor") for i in actions.bot_in_play() + list(ctx.me.discard))
        if doctors:
            yield from actions.gain_glory(doctors)
    yield from actions.log()
    yield from actions.dismiss_duty_officer()


@row(CREW, "with_duty_officer", 4, uses=[A.DISCARD, A.GAIN_CARD, A.DISMISS])
def cargo_officer(ctx, actions):
    """Cargo: Discard the top 3 cards of the Bot deck. Gain a [Research Focus]/[Influence Focus] > Ally. Dismiss Duty
    Officer."""
    yield from actions.discard_top(3)
    yield from actions.gain_card("[Research Focus] / [Influence Focus] > Ally")
    yield from actions.dismiss_duty_officer()


@row(CREW, "with_duty_officer", 5, uses=[A.JUNK, A.GAIN_CARD, A.DISMISS, A.GAIN_SPECIALTY])
def person_officer(ctx, actions):
    """Person: Junk the most valuable card in the Market (ignoring any with tokens). If Bot has 6 or more [Influence],
    gain an [Influence Focus] / Ship / Ally and dismiss Duty Officer; otherwise gain 2 [Influence]."""
    yield from actions.junk()
    if actions.track("influence") >= 6:
        yield from actions.gain_card("[Influence Focus] / Ship / Ally")
        yield from actions.dismiss_duty_officer()
    else:
        yield from actions.gain_specialty("influence", 2)


@row(CREW, "with_duty_officer", 6, uses=[A.LOG, A.REMOVE_AWAY_TEAM, A.TAKE_ENCOUNTER, A.GAIN_SPECIALTY,
                                        A.GAIN_CARD])
def directive_officer(ctx, actions):
    """Directive: If able to do both, log a controlled Location and remove 2 [Away Team] to take top Encounter, then
    log this card. Otherwise gain 1 [Research] and gain a card with any Research, Influence or Military Skill or Focus
    icon."""
    if not (yield from _directive_with_officer(actions)):
        yield from actions.gain_specialty("research", 1)
        yield from actions.gain_card("[Research] / [Influence] / [Military] / [Research Focus] / [Influence Focus] / "
                                     "[Military Focus]")


@row(CREW, "with_duty_officer", 7, uses=[A.LOG, A.GAIN_SPECIALTY, A.GAIN_CARD, A.RESOLVE_CARD])
def encounter_officer(ctx, actions):
    """Encounter: Log the top card of the Bot deck. Gain 1 [Military]. Gain 1 [Influence]. Take an Ally. Resolve the
    top card of the Supplement deck. Log this card."""
    yield from actions.log_top(1)
    yield from actions.gain_specialty("military", 1)
    yield from actions.gain_specialty("influence", 1)
    yield from actions.gain_card("Ally", take=True)
    yield from actions.resolve_supplement_top()
    yield from actions.log()


@row(CREW, "with_duty_officer", 8, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.DISMISS, A.LOG])
def location_officer(ctx, actions):
    """Location: Discard the top 3 cards of the Bot deck. Gain 1 [Influence]. If Duty Officer is Time Travel, dismiss
    it; otherwise log it."""
    yield from actions.discard_top(3)
    yield from actions.gain_specialty("influence", 1)
    officer = actions.duty_officer
    if officer is not None and _has(officer, "Time Travel"):
        yield from actions.dismiss_duty_officer()
    else:
        yield from actions.log_duty_officer()
