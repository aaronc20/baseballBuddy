from src.models.statisticSplits.split import Split

class GameLog(Split):
    def __init__(self, splits, group):
        super().__init__(splits)

        self.pa_or_bf = "plateAppearances" if group == "hitting" else "battersFaced"
        self.split_data = self.splits["splits"]
        self.configured_data = None

    def get_split_data(self):
        return self.configured_data
    
    def get_short_name(self):
        return f"last {self.game_span} games"
    
    def configure(self, games):
        self.get_last_X_games_stats(games)
        self.game_span = games

    def get_last_X_games_stats(self, numGames):
        
        
        cumulative_stats = {
            self.pa_or_bf: 0,
            "atBats": 0,
            "hits": 0,
            "doubles": 0,
            "triples": 0,
            "homeRuns": 0,
            "baseOnBalls": 0,
            "intentionalWalks": 0,
            "sacFlies": 0,
            "hitByPitch": 0,
        }

        for i in range(numGames):
            
            index = -1*i - 1
            
            try:

                stats = self.split_data[index]['stat']
                for k in cumulative_stats.keys():
                    cumulative_stats[k] += stats[k]

            except IndexError:
                break

        calculated_stats = self.calculate_percentage_stats(cumulative_stats)

        
        self.configured_data = cumulative_stats | calculated_stats
    
    def calculate_percentage_stats(self, cumulative_stats):

        hits = cumulative_stats['hits']
        doubles = cumulative_stats['doubles']
        triples = cumulative_stats['triples']
        homeruns = cumulative_stats['homeRuns']
        singles = hits - (doubles + triples + homeruns)

        ab = cumulative_stats['atBats']
        bb = cumulative_stats['baseOnBalls']
        hbp = cumulative_stats['hitByPitch']
        pa = cumulative_stats[self.pa_or_bf]
        sf = cumulative_stats['sacFlies']

        avg = hits/ab
        obp = (hits+bb+hbp) / (ab + bb + hbp + sf)
        slg = (1*singles + 2*doubles + 3*triples + 4*homeruns) / ab
        ops = obp + slg

        return {
            "avg": round(avg, 3),
            "obp": round(obp, 3),
            "slg": round(slg, 3),
            "ops": round(ops, 3),
        }
        


            
            



        


