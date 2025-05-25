# app/models/player.py
from app.api.statsapi import StatsAPI
from functools import reduce

import json

class Player:
    def __init__(self, id: int, name=None):
        self.id = id
        self.name = name

    def get_name(self):
        if not self.name:
            with StatsAPI() as api:

                data = api.fetch(f"v1/people/{self.id}")
                self.name = data["people"][0]["fullName"]

        return self.name

    def get_splits(self, codes=None):

        with StatsAPI() as api:

            code = reduce(lambda acc, item: f"{acc},{item}", codes)
            return api.fetch(f"v1/people/{self.id}/stats?stats=careerStatSplits&sitCodes={code}")
        
    def get_season_splits(self, season=2025, codes=None):

        with StatsAPI() as api:
            
            code = reduce(lambda acc, item: f"{acc},{item}", codes)
            return api.fetch(f"v1/people/{self.id}/stats?stats=statSplits&season={season}&sitCodes={code}")
            
    #
    # create the contents of an html table to display a player's splits.
    # assume the <table></table> header is created, only creating the inside
    #
    def get_split_html_table(self, season=2025, codes=None):

        def split_to_dict(timeframe, splits_data):
            
            if split["stat"]["homeRuns"] == 0:
                abhr = "NA"
            else:
                abhr = split["stat"]["atBats"]/split["stat"]["homeRuns"]
                abhr = f"{abhr:.2f}"
            
            try:
                
                if split["stat"]["plateAppearances"] == 0:
                    hit_percentage = "NA"
                else:
                    hit_percentage = 100*(split["stat"]["hits"]/split["stat"]["plateAppearances"])
                    hit_percentage = f"{hit_percentage:.2f}%"

            except KeyError:

                if split["stat"]["battersFaced"] == 0:
                    hit_percentage = "NA"
                else:
                    hit_percentage = 100*(split["stat"]["hits"]/split["stat"]["battersFaced"])
                    hit_percentage = f"{hit_percentage:.2f}%"

            return {
                "split": f"{timeframe} {split['split']['description'].lower()}",
                "avg": split["stat"]["avg"],
                "obp": split["stat"]["obp"],
                "slg": split["stat"]["slg"],
                "ops": split["stat"]["ops"],
                "ab/hr": abhr,
                "h%": hit_percentage,
            }
        
        stat_names = ["split", "avg", "obp", "slg", "ops", "ab/hr", "h%"]
        splits = []
    
        career_splits_data = self.get_splits(codes)["stats"][0]["splits"]
        for split in career_splits_data:
            splits.append(split_to_dict("career", split))

        # splits.append(split_to_dict("career", career_splits_data["stats"][0]["splits"]))

        splits_data_2025 = self.get_season_splits(2025, codes)["stats"][0]["splits"]
        for split in splits_data_2025:
            splits.append(split_to_dict("2025", split))
        # splits.append(split_to_dict("career", splits_data_2025["stats"][0]["splits"]))


        # splits_data = self.get_season_splits(season, codes)["stats"][0]["splits"]

        # stat_names = ["split", "avg", "obp", "slg", "ops", "ab/hr"]
        # splits = []
        # for split in splits_data:
            
        #     if split["stat"]["homeRuns"] == 0:
        #         abhr = "NA"
        #     else:
        #         abhr = split["stat"]["atBats"]/split["stat"]["homeRuns"]
        #         abhr = f"{abhr:.2f}"

        #     splits.append(
        #         {
        #             "split": split["split"]["description"].lower(),
        #             "avg": split["stat"]["avg"],
        #             "obp": split["stat"]["obp"],
        #             "slg": split["stat"]["slg"],
        #             "ops": split["stat"]["ops"],
        #             "ab/hr": abhr,
        #         }
        #     )

        string_slices = []

        app_string = reduce(lambda acc, elt: f"{acc}<th class=\"border border-black px-4 py-2\">{elt}</th>", stat_names, "")
        string_slices.append(f"<tr>{app_string}</tr>")

        for split in splits:

            row_string = "<tr>"

            for stat_name in split:
                row_string += f"<td>{split[stat_name]}</td>"

            row_string += "</tr>"
            string_slices.append(row_string)

        
                
        # string_slices.append(f"<tr>{reduce(lambda acc, elt: f"{acc}<th class="border border-black px-4 py-2">{elt}</th>", stat_names)}</tr>")

        return "".join(string_slices)
        


        



            







            

    @classmethod
    def search(cls, name: str):
        """Search for players by name and return a list of Player instances."""
        with StatsAPI() as api:
            # Adjusted the endpoint and the parameters
            data = api.fetch("v1/people", {"name": name})
        
        # Check if we got any people back from the API
        if "people" in data:
            return [
                cls(id=p["id"], full_name=p["fullName"])
                for p in data["people"]
            ]
        else:
            return []  # Return an empty list if no results found

    def get_bio(self):
        """Return biographical info for the player."""
        with StatsAPI() as api:
            data = api.fetch(f"people/{self.id}")
        if data.get("people"):
            return data["people"][0]
        return {}
