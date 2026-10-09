"""The Sisko Bot's Automated Command rows. Spec: resources/scans/base_game/command/sisko.md"""

from engine.bot import row
from engine.bot.actions import card_matches
from engine.ops import A

CREW = "sisko"
FRIENDLY = "Starbase > Starfleet > Location"  # "a neutral Starbase > Starfleet > Location"


# ------------------------------------------------------------------ TRAITS

@row(CREW, "traits", 2, uses=[A.GAIN_CARD, A.GAIN_SPECIALTY, A.GAIN_RESOURCE])
def transcendent(ctx, actions):
    """Transcendent: If able, gain a Bajoran > Dominion > Changeling. Otherwise, gain 2 [Military] and 1 [Glory]."""
    if (yield from actions.gain_card("Bajoran > Dominion > Changeling")) is None:
        yield from actions.gain_specialty("military", 2)
        yield from actions.gain_glory(1)


@row(CREW, "traits", 3, uses=[A.DISCARD, A.DEPLOY, A.GAIN_RESOURCE, A.RESOLVE_CARD, A.GAIN_SPECIALTY])
def starbase(ctx, actions):
    """Starbase: Discard the top 3 cards of the Bot deck. If this card is a Ship, deploy this card. Otherwise, gain 1
    [Glory]. If able, resolve a Person from Bot Discard pile. Otherwise gain 2 [Influence]."""
    yield from actions.discard_top(3)
    if actions.is_("Ship"):
        yield from actions.deploy()
    else:
        yield from actions.gain_glory(1)
    if (yield from actions.resolve_from_discard("Person")) is None:
        yield from actions.gain_specialty("influence", 2)


@row(CREW, "traits", 4, uses=[A.GAIN_SPECIALTY, A.TAKE_INCIDENT, A.SEND_AWAY_TEAM, A.ATTACK, A.DISMISS, A.PROMOTE])
def bajoran(ctx, actions):
    """Bajoran: Gain 1 [Influence] and 1 [Military]. Take an Incident. If an Ally is in Bot Discard pile, send 2 [Away
    Team] to a neutral Location. Otherwise, you dismiss (one of) your Duty Officer(s) and the Bot gains 2 [Military].
    If this card is a Person, promote it to Duty Officer."""
    yield from actions.gain_specialty("influence", 1)
    yield from actions.gain_specialty("military", 1)
    yield from actions.take_incident()
    if actions.in_discard("Ally"):
        first = yield from actions.send_away_team()
        if first is not None:
            yield from actions.send_away_team(target=first)
    else:
        if (yield from actions.attack()):
            yield from actions.human_dismisses_duty_officer()
        yield from actions.gain_specialty("military", 2)
    if actions.is_("Person"):
        yield from actions.promote()


@row(CREW, "traits", 5, uses=[A.LOG, A.RESOLVE_CARD, A.PROMOTE])
def changeling_dominion(ctx, actions):
    """Changeling / Dominion: Log the top card of the Bot deck. Resolve the top card of the Bot deck. If this card is
    a Person, promote it to Duty Officer."""
    yield from actions.log_top(1)
    yield from actions.resolve_top()
    if actions.is_("Person"):
        yield from actions.promote()


@row(CREW, "traits", 6, uses=[A.SEND_AWAY_TEAM, A.ATTACK, A.DISCARD, A.DEPLOY, A.ENGAGE, A.GAIN_SPECIALTY])
def attack(ctx, actions):
    """Attack: Send an [Away Team] to a neutral Starbase > Starfleet > Location. If this card is a Ship, you discard a
    card and deploy this Ship; it engages. Otherwise, gain 2 [Military]."""
    yield from actions.send_away_team(FRIENDLY)
    if actions.is_("Ship"):
        if (yield from actions.attack()):
            yield from actions.human_discards()
        yield from actions.deploy()
        yield from actions.engage()
    else:
        yield from actions.gain_specialty("military", 2)


# ------------------------------------------------------------------ SUITS WITH NO DUTY OFFICER

@row(CREW, "no_duty_officer", 1, uses=[A.DISCARD, A.GAIN_CARD, A.RETURN_INCIDENT])
def incident(ctx, actions):
    """Incident: Discard the top card of the Bot deck. Gain a [Military Focus] > [Influence Focus] > Person / Ally.
    Return this card."""
    yield from actions.discard_top(1)
    yield from actions.gain_card("[Military Focus] > [Influence Focus] > Person / Ally")
    yield from actions.return_incident()


@row(CREW, "no_duty_officer", 2, uses=[A.DISCARD, A.DEPLOY, A.EXPLORE, A.SEND_AWAY_TEAM])
def ship(ctx, actions):
    """Ship: Discard the top 3 cards of the Bot deck. Deploy this Ship; it explores. If a Person is in Bot Discard
    pile, send an [Away Team] to a neutral Starbase > Starfleet > Location."""
    yield from actions.discard_top(3)
    yield from actions.deploy()
    yield from actions.explore()
    if actions.in_discard("Person"):
        yield from actions.send_away_team(FRIENDLY)


@row(CREW, "no_duty_officer", 3, uses=[A.GAIN_RESOURCE, A.DISCARD, A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM])
def ally(ctx, actions):
    """Ally: Gain 1 [Glory]. Discard the top 2 cards of the Bot deck. For each Person in Bot Discard pile, gain 1
    [Influence]. For each Ship in Bot Discard pile, send an [Away Team] to a neutral Starbase > Starfleet >
    Location."""
    yield from actions.gain_glory(1)
    yield from actions.discard_top(2)
    people = actions.count_in_discard("Person")
    if people:
        yield from actions.gain_specialty("influence", people)
    for _ in range(actions.count_in_discard("Ship")):
        yield from actions.send_away_team(FRIENDLY)


@row(CREW, "no_duty_officer", 4, uses=[A.DISCARD, A.LOG, A.GAIN_RESOURCE, A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM])
def cargo(ctx, actions):
    """Cargo: Discard the top 2 cards of the Bot deck. If able, log a Person from Bot Discard pile. Gain 1 [Glory].
    Gain 1 [Influence]. Gain 1 [Military]. Send an [Away Team] to a neutral Location."""
    yield from actions.discard_top(2)
    yield from actions.log_from_discard(lambda i: card_matches(i, "Person"))
    yield from actions.gain_glory(1)
    yield from actions.gain_specialty("influence", 1)
    yield from actions.gain_specialty("military", 1)
    yield from actions.send_away_team()


@row(CREW, "no_duty_officer", 5, uses=[A.GAIN_SPECIALTY, A.SEND_AWAY_TEAM, A.PROMOTE])
def person(ctx, actions):
    """Person: Gain 1 [Influence]. Send an [Away Team] to a neutral Location. Promote this card to Duty Officer."""
    yield from actions.gain_specialty("influence", 1)
    yield from actions.send_away_team()
    yield from actions.promote()


@row(CREW, "no_duty_officer", 6, uses=[A.DISCARD, A.LOG, A.SEND_AWAY_TEAM, A.GAIN_SPECIALTY, A.GAIN_CARD])
def directive(ctx, actions):
    """Directive: Discard the top 3 cards of the Bot deck. If able, log a Person from Bot Discard pile to send an [Away
    Team] to a neutral Location. Otherwise, gain 1 [Influence] / [Military] (whichever is lower) and gain a Person."""
    yield from actions.discard_top(3)
    if (yield from actions.log_from_discard(lambda i: card_matches(i, "Person"))) is not None:
        yield from actions.send_away_team()
    else:
        yield from actions.gain_lowest("influence", "military")
        yield from actions.gain_card("Person")


@row(CREW, "no_duty_officer", 7, uses=[A.DISCARD, A.GAIN_CARD, A.LOG])
def encounter(ctx, actions):
    """Encounter: Discard the top 3 cards of the Bot deck. Take an [Influence Focus] > Person. Log this card."""
    yield from actions.discard_top(3)
    yield from actions.gain_card("[Influence Focus] > Person", take=True)
    yield from actions.log()


@row(CREW, "no_duty_officer", 8, uses=[A.LOG, A.DISCARD, A.GAIN_SPECIALTY, A.PUT])
def location(ctx, actions):
    """Location: Log the top card of the Bot deck. Discard the top 3 cards of the Bot deck. Gain 1 [Military]. If able,
    return a Ship from Bot Discard pile to top of the Bot deck."""
    yield from actions.log_top(1)
    yield from actions.discard_top(3)
    yield from actions.gain_specialty("military", 1)
    yield from actions.put_ship_from_discard_on_top()


# ------------------------------------------------------------------ SUITS WITH DUTY OFFICER

@row(CREW, "with_duty_officer", 1, uses=[A.GAIN_CARD, A.GAIN_SPECIALTY, A.RETURN_INCIDENT])
def incident_officer(ctx, actions):
    """Incident: Take a [Military Focus] > Ship > Cargo. Gain 1 [Military]. Return this card."""
    yield from actions.gain_card("[Military Focus] > Ship > Cargo", take=True)
    yield from actions.gain_specialty("military", 1)
    yield from actions.return_incident()


@row(CREW, "with_duty_officer", 2, uses=[A.LOG, A.RESOLVE_CARD, A.DEPLOY, A.EXPLORE, A.SEND_AWAY_TEAM])
def ship_officer(ctx, actions):
    """Ship: If able, log a Starbase in play to resolve the top card of the Supplement deck. Deploy this Ship; it
    explores. Send an [Away Team] to a neutral Location. The Starbase is one of the Bot's own cards in play, the least
    valuable, and never this card."""
    from engine.bot import least_valuable

    bases = [i for i in actions.bot_in_play() if i.uid != actions.this.uid and card_matches(i, "Starbase")]
    base = least_valuable(ctx.state, bases, ctx.me)
    if base is not None and ctx.me.reserve:
        yield from actions.log(base)
        yield from actions.resolve_supplement_top()
    yield from actions.deploy()
    yield from actions.explore()
    yield from actions.send_away_team()


@row(CREW, "with_duty_officer", 3, uses=[A.GAIN_SPECIALTY, A.GAIN_CARD, A.LOG])
def ally_officer(ctx, actions):
    """Ally: Gain 1 [Influence] / [Military] (whichever is lower). Gain a Cargo > Ship / Ally. Log this card."""
    yield from actions.gain_lowest("influence", "military")
    yield from actions.gain_card("Cargo > Ship / Ally")
    yield from actions.log()


@row(CREW, "with_duty_officer", 4, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.GAIN_CARD, A.LOG])
def cargo_officer(ctx, actions):
    """Cargo: Discard the top 3 cards of the Bot deck. Gain 1 [Military]. Gain an [Influence Focus] > [Military Focus]
    > Ship. Log Duty Officer."""
    yield from actions.discard_top(3)
    yield from actions.gain_specialty("military", 1)
    yield from actions.gain_card("[Influence Focus] > [Military Focus] > Ship")
    yield from actions.log_duty_officer()


@row(CREW, "with_duty_officer", 5, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.GAIN_CARD])
def person_officer(ctx, actions):
    """Person: Discard the top 3 cards of the Bot deck. Gain 1 [Influence] / [Military] (whichever is lower). Gain a
    Ship / [Influence Focus]."""
    yield from actions.discard_top(3)
    yield from actions.gain_lowest("influence", "military")
    yield from actions.gain_card("Ship / [Influence Focus]")


@row(CREW, "with_duty_officer", 6, uses=[A.LOG, A.REMOVE_AWAY_TEAM, A.TAKE_ENCOUNTER, A.SEND_AWAY_TEAM,
                                        A.GAIN_SPECIALTY, A.DISMISS])
def directive_officer(ctx, actions):
    """Directive: If able to do both, log a controlled Location (not a Starbase) and remove 2 [Away Team] to take top
    Encounter and log this card. Otherwise, send an [Away Team] to a neutral Location, gain 1 [Influence], and dismiss
    Duty Officer."""
    def plain(loc):
        return not card_matches(loc, "Starbase")

    if any(plain(loc) for loc in ctx.me.locations) and actions.away_teams_on_board() >= 2:
        yield from actions.log_controlled_location(plain)
        yield from actions.remove_away_team(2)
        yield from actions.take_encounter()
        yield from actions.log()
        return
    yield from actions.send_away_team()
    yield from actions.gain_specialty("influence", 1)
    yield from actions.dismiss_duty_officer()


@row(CREW, "with_duty_officer", 7, uses=[A.DISCARD, A.GAIN_SPECIALTY, A.GAIN_CARD])
def encounter_officer(ctx, actions):
    """Encounter: Discard the top card of the Bot deck. Gain 1 [Military]. Gain 1 [Influence]. Take a Ship / Ally."""
    yield from actions.discard_top(1)
    yield from actions.gain_specialty("military", 1)
    yield from actions.gain_specialty("influence", 1)
    yield from actions.gain_card("Ship / Ally", take=True)


@row(CREW, "with_duty_officer", 8, uses=[A.LOG, A.DISCARD, A.GAIN_SPECIALTY])
def location_officer(ctx, actions):
    """Location: Log the top card of the Bot deck. Discard the top 3 cards of the Bot deck. Gain 1 [Influence]. Log
    Duty Officer."""
    yield from actions.log_top(1)
    yield from actions.discard_top(3)
    yield from actions.gain_specialty("influence", 1)
    yield from actions.log_duty_officer()
