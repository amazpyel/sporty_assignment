import allure
from selenium.webdriver.remote.webdriver import WebDriver


def attach_screenshot(driver: WebDriver, name: str) -> None:
    """Attach the current browser view to the Allure report (to the current step, if any)."""
    allure.attach(
        driver.get_screenshot_as_png(), name=name, attachment_type=allure.attachment_type.PNG
    )
