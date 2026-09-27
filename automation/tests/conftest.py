import os
import platform
import sys
from collections.abc import Iterator
from pathlib import Path

import allure
import pytest
from dotenv import load_dotenv
from selenium.webdriver.remote.webdriver import WebDriver

from api_client.betting_client import BettingApiClient
from ui.driver_factory import (
    DEFAULT_BROWSER,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    SUPPORTED_BROWSERS,
    DriverConfig,
    build_driver,
)
from ui.reporting import attach_screenshot

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Real environment variables take precedence over .env.
load_dotenv(PROJECT_ROOT / ".env")


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        pytest.fail(
            f"{name} is not set. Copy .env.example to .env and fill it in, "
            "or export it as an environment variable.",
            pytrace=False,
        )
    return value


def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        default=os.environ.get("BROWSER", DEFAULT_BROWSER),
        help=f"Browser for UI tests: {', '.join(SUPPORTED_BROWSERS)} "
        f"(default: BROWSER env var, else {DEFAULT_BROWSER})",
    )


def pytest_sessionstart(session):
    """
    Generate Allure environment metadata and executor files.
    """
    import json

    results_dir = Path("allure-results")
    results_dir.mkdir(exist_ok=True)

    # Environment properties
    environment_file = results_dir / "environment.properties"
    sports_betting_ui = os.environ.get("BASE_UI_URL", "<not set>")
    sports_betting_api = os.environ.get("BASE_API_URL", "<not set>")

    environment = {
        "Python Version": sys.version.split()[0],
        "OS": f"{platform.system()} {platform.release()}",
        "Sports Betting API": f"{sports_betting_api}",
        "Sports Betting UI": f"{sports_betting_ui}",
        "Browser": session.config.getoption("--browser"),
        "Window Width": os.environ.get("WINDOW_WIDTH", DEFAULT_WINDOW_WIDTH),
        "Window Height": os.environ.get("WINDOW_HEIGHT", DEFAULT_WINDOW_HEIGHT),
    }
    with environment_file.open("w", encoding="utf-8") as f:
        for key, value in environment.items():
            # .properties keys end at the first unescaped space, so escape them.
            escaped_key = key.replace(" ", "\\ ")
            f.write(f"{escaped_key}={value}\n")

    # Executor info - controls report name in Allure
    executor_file = results_dir / "executor.json"
    executor_info = {
        "name": os.getenv("EXECUTOR_NAME", "pytest"),
        "type": os.getenv("EXECUTOR_TYPE", "pytest"),
        "reportName": os.getenv("REPORT_NAME", "Test Suite"),
    }

    with executor_file.open("w", encoding="utf-8") as f:
        json.dump(executor_info, f, indent=2)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):  # noqa: ARG001
    """Attach a browser screenshot to the Allure report when a UI test fails."""
    outcome = yield
    report = outcome.get_result()
    driver = item.funcargs.get("driver")
    if report.when == "call" and report.failed and driver:
        attach_screenshot(driver, "Screenshot on failure")


@pytest.fixture(scope="session")
def base_api_url() -> str:
    return _required_env("BASE_API_URL")


@pytest.fixture(scope="session")
def base_ui_url() -> str:
    return _required_env("BASE_UI_URL")


@pytest.fixture(scope="session")
def user_id() -> str:
    return _required_env("USER_ID")


@pytest.fixture
def api_client(base_api_url, user_id) -> BettingApiClient:
    return BettingApiClient(base_api_url, user_id)


@pytest.fixture(autouse=True)
def reset_balance(api_client: BettingApiClient) -> Iterator[None]:
    """Every test starts and ends with the user's default balance, so tests
    don't leak state into each other or into later manual checks."""
    with allure.step("Reset balance before test"):
        api_client.reset_balance()
    yield
    with allure.step("Reset balance after test"):
        api_client.reset_balance()


@pytest.fixture(scope="session")
def driver_config(pytestconfig) -> DriverConfig:
    return DriverConfig(
        browser=pytestconfig.getoption("--browser").lower(),
        headless=os.environ.get("HEADLESS", "true").lower() != "false",
        window_width=int(os.environ.get("WINDOW_WIDTH", DEFAULT_WINDOW_WIDTH)),
        window_height=int(os.environ.get("WINDOW_HEIGHT", DEFAULT_WINDOW_HEIGHT)),
    )


@pytest.fixture
def driver(driver_config: DriverConfig) -> Iterator[WebDriver]:
    drv = build_driver(driver_config)
    yield drv
    drv.quit()
