"""1SIS05 Orb of the Emissary (Encounter, Development). Spec: resources/scans/base_game/cards/captains/sisko/1SIS05.md
THIS CARD CANNOT BE PLAYED: it has no operations. Once enlisted it scores its 7 VP and lends its traits."""

from engine.cards import development_cost
from engine.ops import Spend

development_cost("1SIS05", Spend(dilithium=3, latinum=3))
