import itertools
import requests
from bs4 import BeautifulSoup
import json
import time
from tqdm import tqdm

# Map PFR team codes to full team names
team_map = {
    'crd': 'Arizona Cardinals', 'atl': 'Atlanta Falcons', 'rav': 'Baltimore Ravens', 'buf': 'Buffalo Bills',
    'car': 'Carolina Panthers', 'chi': 'Chicago Bears', 'cin': 'Cincinnati Bengals', 'cle': 'Cleveland Browns',
    'dal': 'Dallas Cowboys', 'den': 'Denver Broncos', 'det': 'Detroit Lions', 'gnb': 'Green Bay Packers',
    'htx': 'Houston Texans', 'clt': 'Indianapolis Colts', 'jax': 'Jacksonville Jaguars', 'kan': 'Kansas City Chiefs',
    'rai': 'Las Vegas Raiders', 'sdg': 'Los Angeles Chargers', 'ram': 'Los Angeles Rams', 'mia': 'Miami Dolphins',
    'min': 'Minnesota Vikings', 'nwe': 'New England Patriots', 'nor': 'New Orleans Saints', 'nyg': 'New York Giants',
    'nyj': 'New York Jets', 'phi': 'Philadelphia Eagles', 'pit': 'Pittsburgh Steelers', 'sea': 'Seattle Seahawks',
    'sfo': 'San Francisco 49ers', 'tam': 'Tampa Bay Buccaneers', 'oti': 'Tennessee Titans', 'was': 'Washington Commanders'
}

teams = list(team_map.keys())
team_pairs = list(itertools.combinations(teams, 2))
base_url = "https://www.pro-football-reference.com/friv/players-who-played-for-multiple-teams-franchises.fcgi"

player_urls = {}

# Step 1: Collect player profile URLs from team pairs
print("🔍 Gathering player profile links...")
for t1, t2 in tqdm(team_pairs, desc="Finding multi-team players"):
    params = {
        'level': 'franch',
        't1': t1,
        't2': t2,
        't3': '--',
        't4': '--',
        'exclusively': '0'  # not exclusive, allows more than 2 teams
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
    except requests.RequestException:
        continue

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    if not table:
        continue

    for row in table.find_all('tr')[1:]:
        link_tag = row.find('a')
        if link_tag:
            name = link_tag.text.strip()
            href = link_tag.get('href')
            if name not in player_urls:
                player_urls[name] = "https://www.pro-football-reference.com" + href

    time.sleep(1.2)  # avoid rate limiting

# Step 2: Visit each player and extract full team history
print(f"\n🔄 Found {len(player_urls)} unique players. Gathering full team histories...\n")
results = []

for name, url in tqdm(player_urls.items(), desc="Fetching player histories"):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        continue

    soup = BeautifulSoup(response.text, 'html.parser')
    teams_set = set()

    for a_tag in soup.find_all('a'):
        href = a_tag.get('href', '')
        for abbr, full_name in team_map.items():
            if f"/teams/{abbr}/" in href:
                teams_set.add(full_name)

    if teams_set:
        player_data = {
            "Player": name,
            "Teams": sorted(teams_set)
        }
        results.append(player_data)

        # Live terminal output of each result
        print(json.dumps(player_data, indent=2))

    time.sleep(1.2)

# Step 3: Save results to JSON
output_file = "nfl_players_full_team_histories.json"
with open(output_file, "w", encoding='utf-8') as f:
    json.dump(results, f, indent=4)

print(f"\n✅ Done! Saved {len(results)} player records to {output_file}")