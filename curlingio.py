"""
CurlingIO Dataset Builder for xMargin model
-------------------------------------------
This script fetches shot data from the CurlingIO hidden API. It then processes these shots to build
features for the xMargin model, including delta positional shot scoring, ends remaining, and hammer advantages.

"""

import requests
import pandas as pd
from collections import defaultdict
from hammer import hammer_ends_list

# Event Urls
womens = [
    "https://api-curlingio.global.ssl.fastly.net/en/clubs/canada/events/26634", #2026 Scotties
    "https://api-curlingio.global.ssl.fastly.net/en/clubs/canada/events/22098", #2025 Scotties
    "https://api-curlingio.global.ssl.fastly.net/en/clubs/canada/events/18217", #2024 Scotties
    "https://api-curlingio.global.ssl.fastly.net/en/clubs/canada/events/14677"  #2023 Scotties
]

mens = [
    "https://api-curlingio.global.ssl.fastly.net/en/clubs/canada/events/26635", #2026 Brier
    "https://api-curlingio.global.ssl.fastly.net/en/clubs/canada/events/22097", #2025 Brier
    "https://api-curlingio.global.ssl.fastly.net/en/clubs/canada/events/18218", #2024 Brier
    "https://api-curlingio.global.ssl.fastly.net/en/clubs/canada/events/14890"  #2023 Brier
]

mixed = [
    "https://api-curlingio.global.ssl.fastly.net/en/clubs/canada/events/23052"   #2025 trials
]

# Empty dataset template
# Always TeamA - TeamB
data = {
    "womens": {
        "event":[],
        "game":[],  

        "delta_lead": [],
        "delta_second": [],
        "delta_third": [],
        "delta_fourth": [],

        "delta_backend_zeroes": [],
        # "delta_zeroes_hammer": [],
        # "delta_zeroes_steal": [],
        # "delta_ends_hammer": [],

        "ends_remaining": [],
        "team_a_hammer": [],
        "LSFE_a":[],
        "is_even_end":[],

        "a_margin": [],
        "a_win_game": [],

    },

    "mens": {
        "event":[],
        "game":[],  

        "delta_lead": [],
        "delta_second": [],
        "delta_third": [],
        "delta_fourth": [],

        "delta_backend_zeroes": [],
        # "delta_zeroes_hammer": [],
        # "delta_zeroes_steal": [],
        # "delta_ends_hammer": [],

        "ends_remaining": [],
        "team_a_hammer": [],
        "LSFE_a":[],
        "is_even_end":[],

        "a_margin": [],
        "a_win_game": [],
    }
}


# A list of game ids where the data does not work properly.
broken_games = [
    "da838683", # Conceded after 9 ends, but has shot data for 10 ends
    "55095d99", # Abnormally formatted concession
]


# Categories to iterate through
categories = {
    "womens": womens,
    "mens": mens
}

for cat_name, cat in categories.items():
    for event in cat:
        print(event)
        event_data = requests.get(event).json()
        event_stages = event_data['stages']

        for stage in event_stages:
            for game in stage['games']:

                if game['id'] in broken_games:
                    continue

                team_a = game['sides'][0]
                team_b = game['sides'][1]

                # Build the defaultdicts, so that when we append to something that doesn't exist, it creates it.
                team_a_shots = defaultdict(list)
                team_b_shots = defaultdict(list)

                for shot in team_a['shots']:
                    # To avoid any non-integer ratings (usually throw throughs, which do not count as a shot)
                    try:
                        team_a_shots[shot['end_number']].append(int(shot['rating']))
                    except:
                        continue

                for shot in team_b['shots']:
                    try:
                        team_b_shots[shot['end_number']].append(int(shot['rating']))
                    except:
                        continue

                team_a_lsfe = 1 if team_a.get('first_hammer', False) == True else 0
                hammer_ends = hammer_ends_list(a = team_a['end_scores'], b = team_b['end_scores'], lsfe=team_a_lsfe)
               
                # They should already be in order, but just in case.
                ends_in_order = sorted(team_a_shots.keys())
                
                for end in ends_in_order:
                    delta_lead = 0
                    delta_second = 0
                    delta_third = 0
                    delta_fourth = 0
                    
                    delta_backend_zeroes = 0
                    delta_zeroes_hammer = 0
                    delta_zeroes_steal = 0
                    a_margin = 0

                    #Only build our features if its a full end.
                    if len(team_a_shots[end]) == 8 and len(team_b_shots[end]) == 8: 
                        # Add team_a, then subtract team_b
                        delta_lead += (team_a_shots[end][0] + team_a_shots[end][1]) - (team_b_shots[end][0] + team_b_shots[end][1])
                        delta_second += (team_a_shots[end][2] + team_a_shots[end][3]) - (team_b_shots[end][2] + team_b_shots[end][3])
                        delta_third += (team_a_shots[end][4] + team_a_shots[end][5]) - (team_b_shots[end][4] + team_b_shots[end][5])
                        delta_fourth += (team_a_shots[end][6] + team_a_shots[end][7]) - (team_b_shots[end][6] + team_b_shots[end][7])

                        delta_backend_zeroes += team_a_shots[end][4:8].count(0) - team_b_shots[end][4:8].count(0)
                        a_margin += team_a['end_scores'][end-1] - team_b['end_scores'][end-1]


                        # Add all the data
                        data[cat_name]['delta_lead'].append(delta_lead)
                        data[cat_name]['delta_second'].append(delta_second)
                        data[cat_name]['delta_third'].append(delta_third)
                        data[cat_name]['delta_fourth'].append(delta_fourth)
                        data[cat_name]['delta_backend_zeroes'].append(delta_backend_zeroes)

                        data[cat_name]['ends_remaining'].append(10 - int(end)) #When we implement 8 end games, this must be fixed
                        data[cat_name]['a_margin'].append(a_margin)
                        data[cat_name]['event'].append(event_data['name'])
                        data[cat_name]['game'].append(game['id'])
                        data[cat_name]['a_win_game'].append(1 if team_a['score'] > team_b['score'] else 0)
                        data[cat_name]['is_even_end'].append( 1 if int(end) % 2 ==0 else 0)
                        data[cat_name]['LSFE_a'].append(team_a_lsfe)

                        if hammer_ends[end-1] == 'a':
                            data[cat_name]['team_a_hammer'].append('1')
                        else:
                            data[cat_name]['team_a_hammer'].append('0')

    for metric, metdata in data[cat_name].items():
        print(metric, len(metdata))
    cat_data = pd.DataFrame(data[cat_name])
    cat_data.to_csv(f"data/{cat_name}/data.csv", index=False)





                


 



