# app/models/hitter.py
from src.models.player import Player
from src.api.statsapi import StatsAPI

class Batter(Player):

    def get_stats(self, season: int = 2024, stats_type: str = "season"):
        """Fetch stats for this hitter."""
        with StatsAPI() as api:
            data = api.fetch(f"v1/people/{self.id}/stats", {
                "stats": stats_type,
                "group": "hitting",
                "season": season
            })
        return data.get("stats", [])



    def get_home_run_count(self, season: int = 2024):
        """Fetch the home run count for this hitter."""
        stats = self.get_stats(season)
        if stats and stats[0]["splits"]:
            return stats[0]["splits"][0]["stat"].get("homeRuns", 0)
        return 0
