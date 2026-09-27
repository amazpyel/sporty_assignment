"""Pydantic models mirroring docs/open_api_spec.json.

Every API client method validates its response against one of these before
returning it, so a schema drift fails loudly wherever it happens rather than
only inside the two tests that exist today.
"""

from pydantic import BaseModel


class Odds(BaseModel):
    home: float
    draw: float
    away: float


class Match(BaseModel):
    id: str
    competition: str
    kickoffDate: str
    homeTeam: str
    awayTeam: str
    odds: Odds


class Balance(BaseModel):
    balance: float
    currency: str


class PlaceBetResponse(BaseModel):
    message: str
    matchId: str
    selection: str
    stake: float
    odds: float
    payout: float
    balance: float
    currency: str


class Error(BaseModel):
    error: str
    message: str | None = None


class AuthError(BaseModel):
    error: str
