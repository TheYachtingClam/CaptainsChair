"""Helpers shared by Location modules. Registers nothing."""

from engine.ops import Ctx


def no_effect(ctx: Ctx, actions):
    """CONTROL: No effect."""
    return
    yield  # pragma: no cover


def beamed_here(ctx: Ctx):
    return list(ctx.this_card.beamed) if ctx.this_card is not None else []
