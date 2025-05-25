# app/models/schedule.py

from src.api.statsapi import StatsAPI
from src.models.pitcher import Pitcher
from src.models.batter import Batter

BATTER_SPLITS = [None, 'vl', 'vr', 'd7', 'd30']
class Schedule:
    def __init__(self, date=None):
        self.date = date

    def retrieve_games(self):
        with StatsAPI() as api:
            params = {
                "sportId": 1,
                "date": self.date,
            }
            
            games = api.fetch("v1/schedule", params)
            return [Game(game['link'][4:]) for game in games['dates'][0]['games']]

            
    def retrieve_lineups(self):
        with StatsAPI() as api:

            params = {
                "sportId": 1,
                "date": self.date,
            }
            games = api.fetch("v1/schedule", params)

            for game in games['dates'][0]['games']:
                g = Game(game['link'][4:]) # remove "/api" of link
                g.retrieve_lineups()

class Game:
    def __init__(self, link):
        self.link = link
        
        with StatsAPI() as api:
            self.data = api.fetch(self.link)

    def venue(self):
        return self.data['gameData']['venue']['name']
    
    def weather(self):
        try:
            condition = self.data['gameData']['weather']['condition']
        except KeyError:
            condition = "N/A"

        try:
            temp = self.data['gameData']['weather']['temp']
        except KeyError:
            temp = "N/A"
        return f"{condition}, {temp}°F"
    
    def wind(self):
        try:
            wind = self.data['gameData']['weather']['wind']
        except KeyError:
            wind = "N/A"

        return wind

    def start_time(self):
        return self.data['gameData']['datetime']['time'] + self.data['gameData']['datetime']['ampm']
    
    def away_team(self):
        return self.data['gameData']['teams']['away']['name']
    
    def home_team(self):
        return self.data['gameData']['teams']['home']['name']

    def away_starter(self):

        try:
            id = self.data['gameData']['probablePitchers']['away']['id']
            return Pitcher(id)
        except KeyError:
            return None
        return Pitcher(self.data['gameData']['probablePitchers']['away']['id'])
    
    def home_starter(self):

        try:
            id = self.data['gameData']['probablePitchers']['home']['id']
            return Pitcher(id)
        except KeyError:
            return None
        return Pitcher(self.data['gameData']['probablePitchers']['home']['id'])
    
    def get_away_lineup(self):
        lineup = self.data['liveData']['boxscore']['teams']['away']['battingOrder']

        return [Batter(id) for id in lineup]
    
    def get_away_lineup_json(self):

        lineup = self.data['liveData']['boxscore']['teams']['away']['battingOrder']
        
        if lineup:

            json_string = ""

            batters = [Batter(id) for id in lineup]

            for i, batter in enumerate(batters):

                # BATTING Xth string
                json_string += f"<p class=\"text-left\">{i+1}: {batter.get_name()}</p>" 

                # Splits Table
                json_string += f"<table class=\"border border-black mx-auto text-xs\">{batter.get_split_html_table(2025, BATTER_SPLITS)}</table>"


            return json_string

        else:
            return "lineup not released yet"

    def get_home_lineup(self):
        lineup = self.data['liveData']['boxscore']['teams']['home']['battingOrder']

        return [Batter(id) for id in lineup]
    
    def get_home_lineup_json(self):

        lineup = self.data['liveData']['boxscore']['teams']['home']['battingOrder']
        
        if lineup:

            json_string = ""

            batters = [Batter(id) for id in lineup]

            for i, batter in enumerate(batters):

                # BATTING Xth string
                json_string += f"<p class=\"text-left\">{i+1}: {batter.get_name()}</p>" 

                # Splits Table
                json_string += f"<table class=\"border border-black mx-auto text-xs\">{batter.get_split_html_table(2025, BATTER_SPLITS)}</table>"


            return json_string

        else:
            return "lineup not released yet"
    
    def retrieve_game_information(self):
        with StatsAPI() as api:

            data = api.fetch(self.link)

            gameData = data['gameData']

            venue = gameData['venue']['name']
            print(venue)
            import json
            # print(json.dumps(gameData['weather'], indent=6))
            liveData = data['liveData']

    def retrieve_lineups(self):

        with StatsAPI() as api:

            data = api.fetch(self.link)

            gameData = data['gameData']
            liveData = data['liveData']

            print(gameData['teams'])
            print(gameData['probablePitchers'])
            import json


            

            

            

            