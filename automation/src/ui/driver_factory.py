import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def build_chrome_driver() -> webdriver.Chrome:
    """Latest desktop Chrome, headless by default (HEADLESS=false to watch it run)."""
    options = Options()
    if os.environ.get("HEADLESS", "true").lower() != "false":
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)
