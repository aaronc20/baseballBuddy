# app/models/pitcher.py
from src.models.player import Player
from src.api.statsapi import StatsAPI

class Pitcher(Player):
    def get_stats(self, season: int = 2024, stats_type: str = "season"):
        """Fetch stats for this pitcher."""
        with StatsAPI() as api:
            data = api.fetch(f"people/{self.id}/stats", {
                "stats": stats_type,
                "group": "pitching",
                "season": season
            })
        return data.get("stats", [])
    
    def get_name_handedness(self):
        with StatsAPI() as api:
            h = api.fetch(f"v1/people/{self.id}")["people"][0]["pitchHand"]["code"]
            return f"{super().get_name()} ({h})"

    def get_era(self, season: int = 2024):
        """Fetch the ERA for this pitcher."""
        stats = self.get_stats(season)
        if stats and stats[0]["splits"]:
            return stats[0]["splits"][0]["stat"].get("era")
        return None
