import re
from decimal import Decimal

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

DEFAULT_TIMEOUT = 10

Locator = tuple[str, str]

_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")


def parse_currency(text: str) -> Decimal:
    """Extract the first decimal number from a UI string, e.g. "Balance: €117.99" -> 117.99."""
    match = _NUMBER_RE.search(text)
    if not match:
        raise ValueError(f"No numeric value found in {text!r}")
    return Decimal(match.group())


class BasePage:
    """Common interactions for all pages.

    Page objects should go through these helpers instead of calling
    self.driver directly, so waiting and interaction rules (and any future
    browser- or device-specific tweaks) live in one place.
    """

    def __init__(self, driver: WebDriver, base_url: str):
        self.driver = driver
        self.base_url = base_url.rstrip("/")

    def wait(self, timeout: float = DEFAULT_TIMEOUT) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout)

    def open(self, user_id: str) -> None:
        self.driver.get(f"{self.base_url}/?user-id={user_id}")

    def find(self, locator: Locator, timeout: float = DEFAULT_TIMEOUT) -> WebElement:
        """Wait until the element is visible and return it."""
        return self.wait(timeout).until(EC.visibility_of_element_located(locator))

    def text_of(self, locator: Locator) -> str:
        return self.find(locator).text

    def click(self, locator: Locator) -> None:
        self.wait().until(EC.element_to_be_clickable(locator)).click()

    def type_into(self, locator: Locator, text: str) -> None:
        element = self.find(locator)
        element.clear()
        element.send_keys(text)

    def is_present(self, locator: Locator, timeout: float = 0) -> bool:
        """True if the element is in the DOM, waiting up to `timeout` seconds for it."""
        if timeout == 0:
            return len(self.driver.find_elements(*locator)) > 0
        try:
            self.wait(timeout).until(EC.presence_of_element_located(locator))
        except TimeoutException:
            return False
        return True
