from typing import Any, Dict, Optional, TypedDict, Union
from pydantic import BaseModel, Field

class AppState(TypedDict, total=False):
    input: str  # the original user message
    intent: str  # the parsed intent from LLM
    args: Dict[str, Any]  # arguments extracted from LLM for your function
    result: Any  # optional: store the final result (e.g., plot, stats)


class PlyaerStatsInSeasonArguments(BaseModel):
    player_name : str
    season: int

class PlayerStatsAgainstBowlerTypeArguments(BaseModel):
    player_name: str
    bowler_type: str


class BatterStatsAgainstBowlerArguments(BaseModel):
    batter_name: str
    bowler_name: str


class BatterStatsArguments(BaseModel):
    batter_name: str
    opponent_team_name: Optional[str] = None
    city_name: Optional[str] = None
    season: Optional[int] = None
    bowler_name: Optional[str] = None
    bowler_type: Optional[str] = None


class TeamVsTeamArguments(BaseModel):
    team1_name: str
    team2_name: str

class SeasonOverview(BaseModel):
    season: int
# Pydantic
class ParseIntentAndArguments(BaseModel):
    """Parsing intent and User arguments"""

    intent: str = Field(description="Intent of a user")
    arguments: Optional[Union[
        PlayerStatsAgainstBowlerTypeArguments,
        BatterStatsArguments,
        TeamVsTeamArguments,
        SeasonOverview
    ]] = None
