from decimal import Decimal

import allure
import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from api_client.betting_client import BettingApiClient
from ui.bet_flow_result import BetFlowResult
from ui.pages.bet_slip import BetSlip
from ui.pages.match_list_page import MatchListPage
from ui.pages.receipt_modal import ReceiptModal
from ui.reporting import attach_screenshot

STAKE = Decimal("10.00")


@allure.feature("Single Bet Placement")
@allure.severity(allure.severity_level.CRITICAL)
@allure.issue("SBP-2 Balance is not updated after placing a bet")
@allure.issue("SBP-3 Potential payout calculation is incorrect in Bet Receipt")
@allure.issue("SBP-11 Home and away teams are swapped on the bet receipt")
@allure.tag("TCSBP-01")
@pytest.mark.e2e
def test_place_single_bet(
    driver: WebDriver, base_ui_url: str, user_id: str, api_client: BettingApiClient
):
    """Spec sections 2.1-2.4: select odds, stake 10.00, place a bet, see the receipt.

    Expected to currently fail:
    - payout shows stake x 2 instead of stake x odds (SBP-3)
    - the receipt's home/away order can be swapped (SBP-11), and it has no
      dedicated Selection field at all (same underlying gap)
    - the balance is left unchanged instead of being deducted (SBP-2)
    """
    # Precondition "Call POST /api/reset-balance" is done by the reset_balance fixture.
    with allure.step("Precondition: Call GET /api/balance and record the balance as B0"):
        b0 = Decimal(str(api_client.get_balance().balance))

    with allure.step("Precondition: Open the match list and select an upcoming match M"):
        match_list = MatchListPage(driver, base_ui_url)
        match_list.open(user_id)
        match = match_list.find_first_upcoming_match()

    with allure.step(f"1. On match M, click the 1 (home) odds button, O = {match.home_odds}"):
        match_list.click_home_odds(match.match_id)

    slip = BetSlip(driver, base_ui_url)
    with allure.step(f"2. Enter a stake of {STAKE}"):
        slip.enter_stake(str(STAKE))

    with allure.step("3. Read the slip: selection, stake, balance and payout"):
        slip_teams = slip.selection_teams()
        slip_market = slip.selection_market()
        slip_odds = slip.selection_odds()
        slip_total_stake = slip.total_stake()
        slip_potential_payout = slip.potential_payout()
        balance_before_bet = match_list.header_balance()
        attach_screenshot(driver, "Bet slip")

    receipt = ReceiptModal(driver, base_ui_url)
    with allure.step("4. Click Place Bet and read the receipt"):
        slip.click_place_bet()
        placing_state_shown = slip.is_placing()
        receipt.wait_until_visible()
        receipt_bet_id = receipt.bet_id()
        receipt_selection_shown = receipt.shows_selection_field()
        receipt_match = receipt.match()
        receipt_stake = receipt.stake()
        receipt_odds = receipt.odds()
        receipt_payout = receipt.payout()
        receipt_placed_at = receipt.placed_at()
        attach_screenshot(driver, "Bet receipt")

    with allure.step("5. Close the receipt"):
        receipt.close()
        slip_empty_after_close = slip.is_empty()
        balance_after = match_list.header_balance()

    with allure.step(
        "Verify: slip and receipt show the bet with payout 10.00 × O, "
        "slip is empty and balance is B0 − 10.00"
    ):
        # All checks are compared at once so a single run reports every
        # mismatch, not just the first one.
        expected_match_text = f"{match.home_team} vs {match.away_team}"
        expected_payout = (match.home_odds * STAKE).quantize(Decimal("0.01"))
        actual = BetFlowResult(
            slip_teams=slip_teams,
            slip_market=slip_market,
            slip_odds=slip_odds,
            slip_total_stake=slip_total_stake,
            slip_potential_payout=slip_potential_payout,
            balance_before_bet=balance_before_bet,
            placing_state_shown=placing_state_shown,
            receipt_bet_id_present=bool(receipt_bet_id),
            receipt_selection_shown=receipt_selection_shown,
            receipt_match=receipt_match,
            receipt_stake=receipt_stake,
            receipt_odds=receipt_odds,
            receipt_payout=receipt_payout,
            receipt_timestamp_present=bool(receipt_placed_at),
            slip_empty_after_close=slip_empty_after_close,
            balance_after=balance_after,
        )
        expected = BetFlowResult(
            slip_teams=expected_match_text,
            slip_market="Match Winner: Home",
            slip_odds=match.home_odds,
            slip_total_stake=STAKE,
            slip_potential_payout=expected_payout,
            balance_before_bet=b0,
            placing_state_shown=True,
            receipt_bet_id_present=True,
            receipt_selection_shown=True,
            receipt_match=expected_match_text,
            receipt_stake=STAKE,
            receipt_odds=match.home_odds,
            receipt_payout=expected_payout,
            receipt_timestamp_present=True,
            slip_empty_after_close=True,
            balance_after=b0 - STAKE,
        )
        assert actual == expected, (
            f"Placed bet of {STAKE} on {expected_match_text} (home, odds {match.home_odds}) "
            f"does not match the expected result:\n{actual.describe_mismatches(expected)}"
        )
