from decimal import Decimal

from selenium.webdriver.common.by import By

from ui.pages.base_page import BasePage, parse_currency

MODAL_ROOT = (By.ID, "modal-success")


class ReceiptModal(BasePage):
    BET_ID = (By.ID, "modal-success-bet-id")
    MATCH = (By.ID, "modal-success-match")
    STAKE = (By.ID, "modal-success-stake")
    ODDS = (By.ID, "modal-success-odds")
    PAYOUT = (By.ID, "modal-success-payout")
    PLACED_AT = (By.ID, "modal-success-placed-at")
    CLOSE_BUTTON = (By.ID, "modal-success-close")
    LABELS = (By.CSS_SELECTOR, ".modalLabel, .modalMicroLabel, .modalStrong")

    def wait_until_visible(self) -> None:
        self.wait().until(lambda d: d.find_element(*MODAL_ROOT).is_displayed())

    def bet_id(self) -> str:
        return self.driver.find_element(*self.BET_ID).text

    def match(self) -> str:
        return self.driver.find_element(*self.MATCH).text

    def stake(self) -> Decimal:
        return parse_currency(self.driver.find_element(*self.STAKE).text)

    def odds(self) -> Decimal:
        return parse_currency(self.driver.find_element(*self.ODDS).text)

    def payout(self) -> Decimal:
        return parse_currency(self.driver.find_element(*self.PAYOUT).text)

    def placed_at(self) -> str:
        return self.driver.find_element(*self.PLACED_AT).text

    def shows_selection_field(self) -> bool:
        """Spec 2.4 requires a Selection field on the receipt; there's no
        dedicated selector for it, so this scans the modal's own labels."""
        labels = self.driver.find_element(*MODAL_ROOT).find_elements(*self.LABELS)
        return any(label.text.strip().lower() == "selection" for label in labels)

    def close(self) -> None:
        self.driver.find_element(*self.CLOSE_BUTTON).click()
