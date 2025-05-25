from app.models.statisticSplits.split import Split

class GameLog(Split):
    def __init__(self, splits):
        super().__init__(splits)

    def get_last_X_games_stats(self, numGames):

        cumulative_stats = {
            "plateAppearances": 0,
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

                stats = self.splits[index]['stat']
                for k in cumulative_stats.keys():
                    cumulative_stats[k] += stats[k]

            except IndexError:
                break

        calculated_stats = self.calculate_percentage_stats(cumulative_stats)

        
        return cumulative_stats | calculated_stats
    
    def calculate_percentage_stats(self, cumulative_stats):

        hits = cumulative_stats['hits']
        doubles = cumulative_stats['doubles']
        triples = cumulative_stats['triples']
        homeruns = cumulative_stats['homeRuns']
        singles = hits - (doubles + triples + homeruns)

        ab = cumulative_stats['atBats']
        bb = cumulative_stats['baseOnBalls']
        hbp = cumulative_stats['hitByPitch']
        pa = cumulative_stats['plateAppearances']
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
        


            
            



        

def test():

    e = "v1/people/621566/stats?stats=gameLog"

    from app.api.statsapi import StatsAPI

    with StatsAPI() as api:

        r = api.fetch(e)

    splits = r['stats'][0]['splits']
    gls = GameLog(splits)
    import json
    print(json.dumps(gls.get_last_X_games_stats(5), indent=2))

    


test()