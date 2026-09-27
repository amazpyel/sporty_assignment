import allure
import pytest

from api_client.betting_client import BettingApiClient


@allure.feature("Single Bet Placement")
@allure.severity(allure.severity_level.CRITICAL)
@allure.issue(
    "SBP-1 Bet exceeding available balance is accepted by API, resulting in negative balance"
)
@allure.tag("TCSBP-04")
@pytest.mark.api
def test_stake_exceeding_balance_is_rejected(api_client: BettingApiClient):
    """Spec section 4.1: stake must not exceed available balance -> 422 insufficient_balance.

    Expected to currently fail: SBP-1 shows the API accepts the bet and lets
    the balance go negative instead.
    """
    # Precondition "Call POST /api/reset-balance" is done by the reset_balance fixture.
    with allure.step("Precondition: Select an upcoming match"):
        match = api_client.get_first_upcoming_match()

    with allure.step("Precondition: Place a €100.00 bet so that the balance is below €100.00"):
        # Max stake per bet is capped at 100.00 (spec section 3), so testing
        # "balance + 0.01" only isolates the insufficient-balance rule once
        # the balance itself is below that cap.
        api_client.place_bet(match.id, "HOME", stake=100.00)

    with allure.step("Precondition: Call GET /api/balance and record it as B"):
        balance = api_client.get_balance().balance  # ground truth, not a POST response (SBP-8)

    stake = round(balance + 0.01, 2)
    with allure.step(f"1. Send POST /api/place-bet with stake B + 0.01 = {stake}"):
        result = api_client.place_bet(match.id, "HOME", stake=stake)
        error = getattr(result.body, "error", None)

    with allure.step("2. Call GET /api/balance"):
        balance_after = api_client.get_balance().balance

    with allure.step(
        f"Verify: API returns 422 insufficient_balance and balance remains B = {balance}"
    ):
        # There's no endpoint to list bets, so an unchanged balance is the
        # evidence that "no bet is created".
        actual = (result.status_code, error, balance_after)
        expected = (422, "insufficient_balance", balance)
        assert actual == expected, (
            f"Bet with stake {stake} exceeding balance {balance} should be rejected "
            f"with 422 'insufficient_balance' and leave the balance unchanged, but got "
            f"status {result.status_code}, error {error!r}, balance after {balance_after}"
        )
