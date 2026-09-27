from dataclasses import dataclass
from decimal import Decimal

from selenium.webdriver.common.by import By

from ui.pages.base_page import BasePage, parse_currency


@dataclass
class UpcomingMatch:
    match_id: str
    home_team: str
    away_team: str
    home_odds: Decimal


class MatchListPage(BasePage):
    HEADER_BALANCE = (By.ID, "header-balance")
    MATCH_CARD = (By.CSS_SELECTOR, ".matchCard")
    BADGE = (By.CSS_SELECTOR, ".badge")
    TEAM_NAME = (By.CSS_SELECTOR, ".teamName")

    def header_balance(self) -> Decimal:
        text = self.wait().until(lambda d: d.find_element(*self.HEADER_BALANCE)).text
        return parse_currency(text)

    def find_first_upcoming_match(self) -> UpcomingMatch:
        cards = self.wait().until(lambda d: d.find_elements(*self.MATCH_CARD))
        for card in cards:
            if card.find_element(*self.BADGE).text.strip().upper() != "UPCOMING":
                continue
            match_id = card.get_attribute("id").removeprefix("match-card-")
            home_team, away_team = (el.text for el in card.find_elements(*self.TEAM_NAME))
            home_odds_text = self.driver.find_element(
                By.CSS_SELECTOR, f"#odds-{match_id}-home .oddsButtonValue"
            ).text
            return UpcomingMatch(
                match_id=match_id,
                home_team=home_team,
                away_team=away_team,
                home_odds=parse_currency(home_odds_text),
            )
        raise ValueError("No match with an UPCOMING badge found on the page")

    def click_home_odds(self, match_id: str) -> None:
        self.driver.find_element(By.ID, f"odds-{match_id}-home").click()
