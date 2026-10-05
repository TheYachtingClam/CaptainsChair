"""The Soval Bot's Automated Command rows. Spec: resources/scans/to_boldly_go/command/soval.md"""

from engine.bot import LOG_TOP_DISCARDS, row
from engine.ops import A

CREW = "soval"

# Special rule: if a card with Path of Surak would be logged when logging the top card of the Bot deck, discard it.
LOG_TOP_DISCARDS[CREW] = ("Path of Surak",)


# ------------------------------------------------------------------ TRAITS

@row(CREW, "traits", 2, uses=[A.RETURN_INCIDENT, A.RESOLVE_CARD, A.PROMOTE, A.CONTINUE_RESOLUTION])
def telepath(ctx, actions):
    """Telepath: You may return an Incident from your hand or Discard pile. If you do, resolve the top card of the Bot
    deck. If this card is a Person, promote it to Duty Officer. Continue resolution."""
    if (yield from actions.human_may_return_incident()):
        yield from actions.resolve_top()
    if actions.is_("Person"):
        yield from actions.promote()
    yield from actions.continue_resolution()


@row(CREW, "traits", 3, uses=[A.GAIN_RESOURCE, A.GAIN_CARD, A.GAIN_SPECIALTY, A.DISCARD, A.DEPLOY, A.EXPLORE])
def scientist_anomaly(ctx, actions):
    """Scientist / Anomaly: Gain 1 [Glory]. Take [Research] / [Influence] / [Military], if able. Otherwise gain 2
    [Research] and discard the top card of the Bot deck. If this card is a Ship, deploy it; it explores."""
    yield from actions.gain_glory(1)
    taken = yield from actions.gain_card("[Research] / [Influence] / [Military]", take=True,
                                         label="card with a Skill icon")
    if taken is None:
        yield from actions.gain_specialty("research", 2)
        yield from actions.discard_top(1)
    if actions.is_("Ship"):
        yield from actions.deploy()
        yield from actions.explore()


@row(CREW, "traits", 4, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.PROMOTE])
def human_engineer(ctx, actions):
    """Human / Engineer: Discard the top 3 cards of the Bot deck. Gain 1 [Research] / [Influence] / [Military]
    (whichever is lower). If this card is a Person, promote it to Duty Officer."""
    yield from actions.discard_top(3)
    yield from actions.gain_lowest()
    if actions.is_("Person"):
        yield from actions.promote()


@row(CREW, "traits", 5, uses=[A.TAKE_ENCOUNTER, A.RESOLVE_CARD, A.LOG])
def path_of_surak(ctx, actions):
    """Path of Surak: Take top Encounter. If this card is Cargo resolve the top card of the Bot deck and log this
    card."""
    yield from actions.take_encounter()
    if actions.is_("Cargo"):
        yield from actions.resolve_top()
        yield from actions.log()


@row(CREW, "traits", 6, uses=[A.ATTACK, A.REMOVE_AWAY_TEAM, A.SEND_AWAY_TEAM, A.GAIN_SPECIALTY, A.TAKE_CONTROL,
                             A.LOG])
def attack(ctx, actions):
    """Attack: If Bot has 8 or fewer [Military], you remove an [Away Team] from a neutral Location, if able, then send
    a Bot [Away Team] to the same Location, if able. If either option failed, gain 2 [Military]. If Bot has 9+
    [Military], the Bot takes control of a neutral Location (excluding ones you have secured), then log this card."""
    if actions.track("military") <= 8:
        removed = None
        if (yield from actions.attack(removes_away_teams=True)):
            removed = yield from actions.human_removes_away_team(lambda loc: loc in ctx.state.neutral)
        sent = (yield from actions.send_away_team(target=removed)) if removed is not None else None
        if removed is None or sent is None:
            yield from actions.gain_specialty("military", 2)
        return
    from engine.bot import most_valuable

    open_locations = [loc for loc in ctx.state.neutral if not actions.human_secured(loc)]
    target = most_valuable(ctx.state, open_locations, ctx.me)
    if target is not None:
        yield from actions.take_control(target)
    yield from actions.log()


# ------------------------------------------------------------------ SUITS WITH NO DUTY OFFICER

@row(CREW, "no_duty_officer", 1, uses=[A.LOG, A.GAIN_CARD, A.RETURN_INCIDENT])
def incident(ctx, actions):
    """Incident: Log the top card of the Bot deck. Gain a Person. Return this card."""
    yield from actions.log_top(1)
    yield from actions.gain_card("Person")
    yield from actions.return_incident()


@row(CREW, "no_duty_officer", 2, uses=[A.DEPLOY, A.EXPLORE, A.SEND_AWAY_TEAM, A.GAIN_SPECIALTY])
def ship(ctx, actions):
    """Ship: Deploy this Ship; it explores. If Bot has 5+ [Military] send an [Away Team] to a neutral Location.
    Otherwise gain a [Research]."""
    yield from actions.deploy()
    yield from actions.explore()
    if actions.track("military") >= 5:
        yield from actions.send_away_team()
    else:
        yield from actions.gain_specialty("research", 1)


@row(CREW, "no_duty_officer", 3, uses=[A.GAIN_CARD, A.SEND_AWAY_TEAM, A.LOG])
def ally(ctx, actions):
    """Ally: Gain a Human > Person. Send an [Away Team] to a neutral Location. Log this card."""
    yield from actions.gain_card("Human > Person")
    yield from actions.send_away_team()
    yield from actions.log()


@row(CREW, "no_duty_officer", 4, uses=[A.GAIN_SPECIALTY])
def cargo(ctx, actions):
    """Cargo: Gain 1 [Research] / [Military] (whichever is higher)."""
    yield from actions.gain_highest("research", "military")


@row(CREW, "no_duty_officer", 5, uses=[A.LOG, A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM, A.PROMOTE])
def person(ctx, actions):
    """Person: Log the top card of the Bot deck. Gain 1 [Research] / [Military] (whichever is lower). Send an [Away
    Team] to a neutral Location. Promote this card to Duty Officer."""
    yield from actions.log_top(1)
    yield from actions.gain_lowest("research", "military")
    yield from actions.send_away_team()
    yield from actions.promote()


@row(CREW, "no_duty_officer", 6, uses=[A.GAIN_CARD, A.TAKE_INCIDENT])
def directive(ctx, actions):
    """Directive: Gain a [Research Focus] > Scientist / Telepath > Ally and gain an Incident."""
    yield from actions.gain_card("[Research Focus] > Scientist / Telepath > Ally")
    yield from actions.gain_incident()


@row(CREW, "no_duty_officer", 7, uses=[A.GAIN_SPECIALTY, A.DISCARD])
def encounter(ctx, actions):
    """Encounter: Gain 1 [Research]. Discard the top card of the Supplement deck."""
    yield from actions.gain_specialty("research", 1)
    yield from actions.discard_supplement_top()


@row(CREW, "no_duty_officer", 8, uses=[A.DISCARD, A.GAIN_RESOURCE])
def location(ctx, actions):
    """Location: Discard the top 3 cards of the Bot deck. Gain 1 [Glory]."""
    yield from actions.discard_top(3)
    yield from actions.gain_glory(1)


# ------------------------------------------------------------------ SUITS WITH DUTY OFFICER

def _officer_is_vulcan(actions) -> bool:
    from engine.ops import card

    officer = actions.duty_officer
    return officer is not None and "Vulcan" in card(officer).traits


@row(CREW, "with_duty_officer", 1, uses=[A.LOG, A.GAIN_SPECIALTY, A.RETURN_INCIDENT])
def incident_officer(ctx, actions):
    """Incident: Log the top card of the Bot deck. Gain 1 [Research]. Gain 1 [Military]. Return this card."""
    yield from actions.log_top(1)
    yield from actions.gain_specialty("research", 1)
    yield from actions.gain_specialty("military", 1)
    yield from actions.return_incident()


@row(CREW, "with_duty_officer", 2, uses=[A.DEPLOY, A.EXPLORE, A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM])
def ship_officer(ctx, actions):
    """Ship: Deploy this Ship; it explores. Gain 1 [Military]. Send an [Away Team] to a neutral Location."""
    yield from actions.deploy()
    yield from actions.explore()
    yield from actions.gain_specialty("military", 1)
    yield from actions.send_away_team()


@row(CREW, "with_duty_officer", 3, uses=[A.GAIN_CARD, A.LOG])
def ally_officer(ctx, actions):
    """Ally: Gain a Scientist / Telepath > Ship > Ally. If Duty Officer is not Vulcan, log Duty Officer. Log this
    card."""
    yield from actions.gain_card("Scientist / Telepath > Ship > Ally")
    if not _officer_is_vulcan(actions):
        yield from actions.log_duty_officer()
    yield from actions.log()


@row(CREW, "with_duty_officer", 4, uses=[A.GAIN_CARD, A.DISMISS])
def cargo_officer(ctx, actions):
    """Cargo: Gain Scientist / Anomaly / Engineer > Ally, including from Junk. Dismiss Duty Officer."""
    yield from actions.gain_card("Scientist / Anomaly / Engineer > Ally", including_junk=True)
    yield from actions.dismiss_duty_officer()


@row(CREW, "with_duty_officer", 5, uses=[A.PUT, A.GAIN_CARD, A.DISMISS])
def person_officer(ctx, actions):
    """Person: If Ship is in Bot Discard, put it on top of the Bot deck. Gain a [Research Focus] > [Military Focus] >
    [Influence Focus] > Ship and dismiss Duty Officer."""
    ship_card = actions.topmost_in_discard("Ship")
    if ship_card is not None:
        yield from actions.put_on_top(ship_card)
    yield from actions.gain_card("[Research Focus] > [Military Focus] > [Influence Focus] > Ship")
    yield from actions.dismiss_duty_officer()


@row(CREW, "with_duty_officer", 6, uses=[A.GAIN_SPECIALTY, A.DISCARD, A.GAIN_RESOURCE])
def directive_officer(ctx, actions):
    """Directive: Gain 1 [Research]. Gain 1 [Influence] / [Military] (whichever is lower). If Duty Officer is Vulcan,
    discard the top 2 cards of the Bot deck; otherwise gain 1 [Glory]."""
    yield from actions.gain_specialty("research", 1)
    yield from actions.gain_lowest("influence", "military")
    if _officer_is_vulcan(actions):
        yield from actions.discard_top(2)
    else:
        yield from actions.gain_glory(1)


@row(CREW, "with_duty_officer", 7, uses=[A.GAIN_SPECIALTY, A.RESOLVE_CARD, A.LOG])
def encounter_officer(ctx, actions):
    """Encounter: Gain 1 [Research]. Gain 1 [Influence]. Resolve the top card of the Supplement deck. Log this card."""
    yield from actions.gain_specialty("research", 1)
    yield from actions.gain_specialty("influence", 1)
    yield from actions.resolve_supplement_top()
    yield from actions.log()


@row(CREW, "with_duty_officer", 8, uses=[A.GAIN_SPECIALTY, A.GAIN_CARD, A.LOG])
def location_officer(ctx, actions):
    """Location: Gain 1 [Influence]. Gain a [Research Focus] > Starfleet > Cargo. Log Duty Officer."""
    yield from actions.gain_specialty("influence", 1)
    yield from actions.gain_card("[Research Focus] > Starfleet > Cargo")
    yield from actions.log_duty_officer()
