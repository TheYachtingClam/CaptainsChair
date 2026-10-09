"""1SHR08 Andorian Ale (Cargo, Development). Spec: resources/scans/base_game/cards/captains/shran/1SHR08.md"""

from engine.cards import development_cost, operation
from engine.ops import A, Spend

development_cost("1SHR08", Spend(dilithium=1, latinum=1))


@operation("1SHR08", 0, uses=[A.SCAN, A.JUNK], cost=[Spend(latinum=2)])
def toast(ctx, actions):
    """PLAY: Spend 2 [Latinum] to scan 1 of Ally, including from the Junk. Junk a card from the Market."""
    yield from actions.scan(1, ["Ally"], include_junk=True)
    yield from actions.junk()
