import itertools
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

pfr_teams = [
    'crd', 'atl', 'rav', 'buf', 'car', 'chi', 'cin', 'cle',
    'dal', 'den', 'det', 'gnb', 'htx', 'clt', 'jax', 'kan',
    'rai', 'sdg', 'ram', 'mia', 'min', 'nwe', 'nor', 'nyg',
    'nyj', 'phi', 'pit', 'sea', 'sfo', 'tam', 'oti', 'was'
]

team_pairs = list(itertools.combinations(pfr_teams, 2))

base_url = "https://www.pro-football-reference.com/friv/players-who-played-for-multiple-teams-franchises.fcgi"

results = []

for t1, t2 in team_pairs:
    params = {
        'level': 'franch',
        't1': t1,
        't2': t2,
        't3': '--',
        't4': '--',
        'exclusively': '1'
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching data for {t1} & {t2}: {e}")
        continue

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    if not table:
        continue

    for row in table.find_all('tr')[1:]:  # skip header
        cells = row.find_all('td')
        if cells:
            player = cells[0].text.strip()
            results.append({
                'Player': player,
                'Team1': t1,
                'Team2': t2
            })

    print(f"Processed {t1.upper()} & {t2.upper()} - found {len(results)} players so far")
    time.sleep(1.5)  # Be polite and avoid rate limits

# Save to CSV
df = pd.DataFrame(results)
df.to_csv("pfr_multi_team_players.csv", index=False)
