from decimal import Decimal

from selenium.webdriver.common.by import By

from ui.pages.base_page import BasePage, parse_currency

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
        stake_input = self.driver.find_element(*self.STAKE_INPUT)
        stake_input.clear()
        stake_input.send_keys(value)

    def selection_teams(self) -> str:
        return self.driver.find_element(*self.SELECTION_TEAMS).text

    def selection_market(self) -> str:
        return self.driver.find_element(*self.SELECTION_MARKET).text

    def selection_odds(self) -> Decimal:
        return parse_currency(self.driver.find_element(*self.SELECTION_ODDS).text)

    def total_stake(self) -> Decimal:
        return parse_currency(self.driver.find_element(*self.TOTAL_STAKE).text)

    def potential_payout(self) -> Decimal:
        return parse_currency(self.driver.find_element(*self.POTENTIAL_PAYOUT).text)

    def click_place_bet(self) -> None:
        self.driver.find_element(*self.PLACE_BET_BUTTON).click()

    def is_placing(self) -> bool:
        """Best-effort check for the transient "Placing..." loading state.

        Read once, right after click_place_bet(), with no extra sleep: on a
        fast/mocked API this state can resolve before a polled wait would
        even run, so a wait here would mask the very thing being checked.
        """
        button = self.driver.find_element(*self.PLACE_BET_BUTTON)
        return PLACING_BUTTON_CLASS in (button.get_attribute("class") or "")

    def is_empty(self) -> bool:
        elements = self.driver.find_elements(*self.EMPTY_STATE)
        return len(elements) > 0
