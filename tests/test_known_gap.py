"""Known design gap: sticky auth vs restated auth after reversal.

This test FAILS on purpose. It reveals that reversing E7 does not rewrite
Auth-B's apply-time denial. A restatement model would re-check Auth-B after
E9 against restored available balance and approve the hold; our append-only
sticky-outcome model keeps the original REJECTED decision forever.

What it reveals: reversal restores ledger/fee projections, but prior
authorization outcomes are historical facts in the source log — they are not
re-derived when later compensating entries arrive.
"""

from ledger.engine import Ledger
from ledger.events import AuthStatus
from ledger.stream import phase6_stream


def test_restated_auth_b_would_approve_after_e9_but_sticky_denies():
    """FAILS: expects restated APPROVED+hold; design keeps sticky REJECTED."""
    ledger = Ledger()
    for ev in phase6_stream():
        ledger.apply(ev)

    # Hypothetical restatement: after E9, available (pre-interest) is 465.00,
    # so Auth-B's AED 90.00 hold would clear the available-balance check.
    assert ledger.active_holds_minor("ACC-001") == 0
    assert ledger._closing_before_interest("ACC-001", 6).minor == 46500

    # Restatement expectation (what this test asserts — and our design refuses):
    assert ledger.auths["Auth-B"].status == AuthStatus.APPROVED
    assert ledger.active_holds_minor("ACC-001") == 9000
