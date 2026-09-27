from dataclasses import dataclass, fields
from decimal import Decimal


@dataclass
class BetFlowResult:
    """What the UI showed at each point of the single-bet flow (TCSBP-01).

    The test builds one from the page and one from expectations and compares
    them at once, so a single run reports every mismatch.
    """

    slip_teams: str
    slip_market: str
    slip_odds: Decimal
    slip_total_stake: Decimal
    slip_potential_payout: Decimal
    balance_before_bet: Decimal
    placing_state_shown: bool
    receipt_bet_id_present: bool
    receipt_selection_shown: bool
    receipt_match: str
    receipt_stake: Decimal
    receipt_odds: Decimal
    receipt_payout: Decimal
    receipt_timestamp_present: bool
    slip_empty_after_close: bool
    balance_after: Decimal

    def describe_mismatches(self, expected: "BetFlowResult") -> str:
        """One line per field that differs from `expected`."""
        return "\n".join(
            f"  {f.name}: expected {getattr(expected, f.name)!r}, got {getattr(self, f.name)!r}"
            for f in fields(self)
            if getattr(self, f.name) != getattr(expected, f.name)
        )
