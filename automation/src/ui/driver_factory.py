"""Builds WebDriver instances for the browsers the suite can run on.

To add a browser (or a device profile, Grid/cloud target, ...), write one
builder that turns a DriverConfig into a WebDriver and register it in
BUILDERS. Nothing else in the framework needs to change: page objects only
depend on the generic WebDriver interface.
"""

from collections.abc import Callable
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver


@dataclass(frozen=True)
class DriverConfig:
    browser: str
    headless: bool
    window_width: int
    window_height: int


def _chrome(config: DriverConfig) -> WebDriver:
    options = webdriver.ChromeOptions()
    if config.headless:
        options.add_argument("--headless=new")
    options.add_argument(f"--window-size={config.window_width},{config.window_height}")
    return webdriver.Chrome(options=options)


BUILDERS: dict[str, Callable[[DriverConfig], WebDriver]] = {
    "chrome": _chrome,
}

SUPPORTED_BROWSERS = tuple(BUILDERS)
DEFAULT_BROWSER = "chrome"
DEFAULT_WINDOW_WIDTH = 1920
DEFAULT_WINDOW_HEIGHT = 1080


def build_driver(config: DriverConfig) -> WebDriver:
    try:
        builder = BUILDERS[config.browser]
    except KeyError:
        raise ValueError(
            f"Unsupported browser {config.browser!r}. Supported: {', '.join(SUPPORTED_BROWSERS)}"
        ) from None
    return builder(config)
