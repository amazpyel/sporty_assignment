from decimal import Decimal

from selenium.webdriver.common.by import By

from ui.pages.base_page import DEFAULT_TIMEOUT, BasePage, parse_currency

PLACING_BUTTON_CLASS = "placeBetButtonPlacing"


class BetSlip(BasePage):
    STAKE_INPUT = (By.ID, "bet-slip-stake-input")
    PLACE_BET_BUTTON = (By.ID, "bet-slip-place-bet")
    SELECTION_TEAMS = (By.CSS_SELECTOR, ".betSelectionTeams")
    SELECTION_MARKET = (By.CSS_SELECTOR, ".betSelectionMarket")
    SELECTION_ODDS = (By.CSS_SELECTOR, ".betSelectionOdds")
    TOTAL_STAKE = (By.ID, "bet-slip-total-stake")
    POTENTIAL_PAYOUT = (By.ID, "bet-slip-potential-payout")
    EMPTY_STATE = (By.CSS_SELECTOR, ".betSlipBodyEmpty")

    def enter_stake(self, value: str) -> None:
        self.type_into(self.STAKE_INPUT, value)

    def selection_teams(self) -> str:
        return self.text_of(self.SELECTION_TEAMS)

    def selection_market(self) -> str:
        return self.text_of(self.SELECTION_MARKET)

    def selection_odds(self) -> Decimal:
        return parse_currency(self.text_of(self.SELECTION_ODDS))

    def total_stake(self) -> Decimal:
        return parse_currency(self.text_of(self.TOTAL_STAKE))

    def potential_payout(self) -> Decimal:
        return parse_currency(self.text_of(self.POTENTIAL_PAYOUT))

    def click_place_bet(self) -> None:
        self.click(self.PLACE_BET_BUTTON)

    def is_placing(self) -> bool:
        """Best-effort check for the transient "Placing..." loading state.

        Read once, right after click_place_bet(), with no extra sleep: on a
        fast/mocked API this state can resolve before a polled wait would
        even run, so a wait here would mask the very thing being checked.
        That's why this reads the driver directly instead of using find().
        """
        button = self.driver.find_element(*self.PLACE_BET_BUTTON)
        return PLACING_BUTTON_CLASS in (button.get_attribute("class") or "")

    def is_empty(self) -> bool:
        return self.is_present(self.EMPTY_STATE, timeout=DEFAULT_TIMEOUT)
