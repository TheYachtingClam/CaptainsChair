"""3RIK02 U.S.S. Titan (Ship). Its first three operations are registered with Pike's U.S.S. Enterprise.
Spec: resources/scans/second_contact/cards/captains/william riker/3RIK02.md"""

from engine.cards import operation
from engine.cards.to_boldly_go.uss_shenzhou import promote
from engine.ops import A

from ._util import is_suit

operation("3RIK02", 3, uses=[A.PROMOTE], requires=lambda ctx: any(is_suit(i, "Person") for i in ctx.me.hand))(promote)
