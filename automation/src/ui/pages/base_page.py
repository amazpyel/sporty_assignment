import re
from decimal import Decimal

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

DEFAULT_TIMEOUT = 10

_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")


def parse_currency(text: str) -> Decimal:
    """Extract the first decimal number from a UI string, e.g. "Balance: €117.99" -> 117.99."""
    match = _NUMBER_RE.search(text)
    if not match:
        raise ValueError(f"No numeric value found in {text!r}")
    return Decimal(match.group())


class BasePage:
    def __init__(self, driver: WebDriver, base_url: str):
        self.driver = driver
        self.base_url = base_url.rstrip("/")

    def wait(self, timeout: float = DEFAULT_TIMEOUT) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout)

    def open(self, user_id: str) -> None:
        self.driver.get(f"{self.base_url}/?user-id={user_id}")
