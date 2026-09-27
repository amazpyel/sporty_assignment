from dataclasses import dataclass
from datetime import date, datetime

from api_client.base_client import BaseApiClient
from models.betting import Balance, Error, Match, PlaceBetResponse


@dataclass
class PlaceBetResult:
    status_code: int
    body: PlaceBetResponse | Error


class BettingApiClient(BaseApiClient):
    """Every method validates the response against its OpenAPI schema before
    returning it — schema validation is the default, not opt-in per test."""

    def get_matches(self) -> list[Match]:
        response = self.get("/matches")
        response.raise_for_status()
        return [Match.model_validate(item) for item in response.json()]

    def get_first_upcoming_match(self, today: date | None = None) -> Match:
        """First match whose kickoff is today or later, in API list order.

        The UI test instead relies on the app's own "UPCOMING" badge, since
        that's what a real user sees.
        """
        reference_day = today or date.today()
        for match in self.get_matches():
            kickoff = datetime.strptime(match.kickoffDate, "%Y-%m-%d").date()
            if kickoff >= reference_day:
                return match
        raise ValueError("No upcoming match found in the match list")

    def get_balance(self) -> Balance:
        response = self.get("/balance")
        response.raise_for_status()
        return Balance.model_validate(response.json())

    def reset_balance(self) -> Balance:
        response = self.post("/reset-balance")
        response.raise_for_status()
        return Balance.model_validate(response.json())

    def place_bet(self, match_id: str, selection: str, stake: float) -> PlaceBetResult:
        response = self.post(
            "/place-bet",
            json={"matchId": match_id, "selection": selection, "stake": stake},
        )
        body: PlaceBetResponse | Error
        if response.status_code == 200:
            body = PlaceBetResponse.model_validate(response.json())
        else:
            body = Error.model_validate(response.json())
        return PlaceBetResult(status_code=response.status_code, body=body)
