"""1SEL08 Forced Singularity (Cargo, Development). Spec: resources/scans/base_game/cards/captains/sela/1SEL08.md
The operations are those of the Market card (2CAR06) and are registered with it; only the development cost is here."""

from engine.cards import development_cost
from engine.ops import DismissFromPlay

from ._util import is_suit

development_cost("1SEL08", DismissFromPlay(lambda ctx, i: is_suit(i, "Ship") and i in ctx.me.fleet, "a deployed Ship"))
