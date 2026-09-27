import os
import platform
import sys
from collections.abc import Iterator
from pathlib import Path

import allure
import pytest
from dotenv import load_dotenv

from api_client.betting_client import BettingApiClient
from ui.driver_factory import build_chrome_driver

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCREENSHOT_DIR = PROJECT_ROOT / "reports" / "screenshots"

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


def pytest_sessionstart(session):  # noqa: ARG001
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


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):  # noqa: ARG001
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


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


@pytest.fixture
def driver(request) -> Iterator:
    drv = build_chrome_driver()
    yield drv
    failed = getattr(request.node, "rep_call", None) is not None and request.node.rep_call.failed
    if failed:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        screenshot = SCREENSHOT_DIR / f"{request.node.name}.png"
        drv.save_screenshot(str(screenshot))
        allure.attach.file(
            str(screenshot), name="screenshot", attachment_type=allure.attachment_type.PNG
        )
    drv.quit()
