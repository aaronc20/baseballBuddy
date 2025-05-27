from src.models.schedule import Schedule

from colorama import Fore
#
# V2 of todays_slate
# emphasis on runtime (sacrificing raw compute time for http processing speed)
# 
from jinja2 import Environment, FileSystemLoader
import os
# delete later once implemented into controllers
from src.api.statsapi import StatsAPI
from src.models.statisticSplits.gamelog import GameLog
from src.models.statisticSplits.stat_splits import StatSplits
from src.models.statisticSplits.career_stat_splits import CareerStatSplits

from tabulate import tabulate
from functools import reduce

def create_table_row(s):
    split_data = s.get_split_data()

    hr_p = "N/A"
    h_p = "N/A"

    if split_data['plateAppearances'] != 0:
        hr_p = f"{(100*split_data['homeRuns']/split_data['plateAppearances']):.2f}"
        h_p = f"{(100*split_data['hits']/split_data['plateAppearances']):.2f}"

        if float(h_p) > 25:
            h_p = f'<span style="color:green"><strong>{h_p}</strong></span>'
        elif float(h_p) < 20:
            h_p = f'<span style="color:red"><strong>{h_p}</strong></span>'

    else:
        hr_p = "N/A"
        h_p = "N/A"

    return {
        "split": s.get_short_name(),
        "pa": split_data['plateAppearances'],
        'avg': split_data['avg'],
        'obp': split_data['obp'],
        'slg': split_data['slg'],
        'ops': split_data['ops'],
        'hr%': hr_p,
        'h%': h_p,
    }
    
def update_slate():

    games = Schedule().retrieve_games()
    games_data = []

    for i, game in enumerate(games):

        starters = {
            "away": game.away_starter(),
            "home": game.home_starter(),
        }

        
        if starters['away'] or starters['home']:
            # create hydration

            endpoint = "v1/people"
            
            sps = []
            for starter in [starters['away'], starters['home']]:
                if starter:
                    sps.append(str(starter.id))

            
            personIds = ",".join(sps)
            print(personIds)
            hydration = "stats(group=pitching,type=[statSplits,careerStatSplits],sitCodes=[h,a,vl,vr])"

            pitcher_hydration_params = {
                "personIds": personIds,
                "hydrate": hydration,
            }

            with StatsAPI() as api:
                r = api.fetch(endpoint, pitcher_hydration_params)

            
            import json
            
            peoples = r['people']

            away_ps_table = None
            home_ps_table = None
            for people in peoples:

                table = []
                for stat in people['stats']:
                    
                    statType = stat['type']['displayName']
                    # make html tables here

                    for person_split in stat['splits']:

                        split = person_split['split']['description']
                        
                        stat = person_split['stat']

                        hr_p = "N/A"
                        h_p = "N/A"

                        if stat['battersFaced'] != 0:

                            hr_p = f"{(100*stat['homeRuns']/stat['battersFaced']):.2f}"
                            h_p = f"{(100*stat['hits']/stat['battersFaced']):.2f}"


                            
                        row_data = {
                            "split": f"{statType} {split}",
                            "pa": stat['battersFaced'],
                            'avg': stat['avg'],
                            'obp': stat['obp'],
                            'slg': stat['slg'],
                            'ops': stat['ops'],
                            'hr%': hr_p,
                            'h%': h_p,
                        }

                        table.append(row_data)

                
                table = tabulate(table, tablefmt='html', headers='keys')
                table = table.replace("<table>", "").replace("</table>", "")

                
                if game.away_starter() and people['id'] == game.away_starter().id:
                    away_ps_table = table
                elif game.home_starter() and people['id'] == game.home_starter().id:
                    home_ps_table = table
                else:
                    print("NO PITCHERS")


        lineups = {
            "away": game.get_away_lineup(),
            "home": game.get_home_lineup(),
        }

        # create hydration

        if lineups['away'] or lineups['home']:
            personIds = ",".join([str(person.id) for person in (lineups['away'] + lineups['home'])])
            print(personIds)
            # hitting_hydration = "stats(group=hitting,type=[statSplits,careerStatSplits],sitCodes=[h,a,vl,vr])"
            hitting_hydration = "stats(group=hitting,type=[statSplits,careerStatSplits,gameLog],sitCodes=[h,a,vl,vr],seasons=[2025])"
            # hitting_hydration = "stats(group=hitting,type=gameLog)"

            batter_hydration_params = {
                "personIds": personIds,
                "hydrate": hitting_hydration,
            }

            with StatsAPI() as api:
                r = api.fetch(endpoint, batter_hydration_params)

            batter_data = r['people']
            batter_tables = {}
            batter_handedness = {}

            for batter in batter_data:
                batter_id = batter['id']
                batter_handedness[batter_id] = batter['batSide']['code']

                table = []
                for stat in batter['stats']:

                    statType = stat['type']['displayName']
                    statGroup = stat['group']['displayName']

                    if statType == "gameLog":
                        
                        print("gamelogggG")
                        s = GameLog(stat, statGroup)

                        for game_span in [7,15,30]:
                            s.configure(game_span)
                            table.append(create_table_row(s))

                    elif statType == "statSplits":
                        
                        for split in stat['splits']:
                            
                            s = StatSplits(split, statGroup)
                            
                            table.append(create_table_row(s))
                      
                    elif statType == "careerStatSplits":
                        
                        for split in stat['splits']:
                            
                            s = CareerStatSplits(split, statGroup)

                            table.append(create_table_row(s))


                    # elif statType == "careerStatSplits":
                    #     split_data = CareerStatSplits(stat)
                        
                    # print(type(s))
                    # split_data = s.get_split_data()

                    # if split_data['plateAppearances'] != 0:
                    #     hr_p = f"{(100*split_data['homeRuns']/split_data['plateAppearances']):.2f}"
                    #     h_p = f"{(100*split_data['hits']/split_data['plateAppearances']):.2f}"
                    # else:
                    #     hr_p = "N/A"
                    #     h_p = "N/A"

                    # row_data = {
                    #     "split": s.split_short_name(),
                    #     "pa": split_data['plateAppearances'],
                    #     'avg': split_data['avg'],
                    #     'obp': split_data['obp'],
                    #     'slg': split_data['slg'],
                    #     'ops': split_data['ops'],
                    #     'hr%': hr_p,
                    #     'h%': h_p,
                    # }

                    # table.append(row_data)

                table = tabulate(table, tablefmt='unsafehtml', headers='keys')
                table = table.replace("<table>", "<table class=\"border border-black mx-auto text-xs\">")

                batter_tables[batter_id] = table
            
            away_lineup_html = "" if lineups['away'] else "Lineup Not Released"
            for order_spot, away_batter in enumerate(lineups['away']):
                away_lineup_html += f"{order_spot}: {away_batter.get_name()} ({batter_handedness[away_batter.id]})<br>{batter_tables[away_batter.id]}"
                

            home_lineup_html = "" if lineups['home'] else "Lineup Not Released"
            for order_spot, home_batter in enumerate(lineups['home']):
                home_lineup_html += f"{order_spot}: {home_batter.get_name()} ({batter_handedness[home_batter.id]})<br>{batter_tables[home_batter.id]}"

        else:

            away_lineup_html = "Lineup Not Released Yet"
            home_lineup_html = "Lineup Not Released Yet"

        games_data.append(
            {
                "away_team": game.away_team(),
                "home_team": game.home_team(),
                "venue": game.venue(),
                "time": game.start_time(),
                "weather": game.weather(),
                "wind": game.wind(),
                "away_pitcher": game.away_starter().get_name_handedness() if game.away_starter() else "None",
                "home_pitcher": game.home_starter().get_name_handedness() if game.home_starter() else "None",
                "away_pitcher_splits": away_ps_table,
                "home_pitcher_splits": home_ps_table,
                "away_lineup": away_lineup_html,
                "home_lineup": home_lineup_html,

            }
        )
                    

        
        # Get the directory where this script file is located
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')

    # Set up Jinja2 to load from that directory
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("template.html")

    html_output = template.render(games=games_data)

    # Save or display it

    output_dir = os.path.join(os.path.dirname(__file__), 'templates/outputs/todays_slate.html')
    with open(output_dir, "w") as f:
        f.write(html_output)

import time

while True:
    update_slate()
    time.sleep(1800)
