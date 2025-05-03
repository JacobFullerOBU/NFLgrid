import itertools
import requests
import json
import os
import time
from bs4 import BeautifulSoup, Comment
from tqdm import tqdm

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

def get_table_from_comments(soup, table_id):
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        if table_id in comment:
            comment_soup = BeautifulSoup(comment, 'html.parser')
            return comment_soup.find('table', {'id': table_id})
    return None

def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

base_url = "https://www.pro-football-reference.com/friv/players-who-played-for-multiple-teams-franchises.fcgi"

# Set up team combinations
teams = list(team_map.keys())
team_pairs = list(itertools.combinations(teams, 2))

# Load progress and results
progress = load_json("progress.json", {"checked_combinations": [], "fetched_players": []})
results = load_json("results.json", [])

# Resume from last saved state
checked_combinations = set(tuple(pair) for pair in progress["checked_combinations"])
fetched_players = set(progress["fetched_players"])

print("🔄 Resuming from previous progress...")
for t1, t2 in tqdm(team_pairs, desc="Team combos"):
    if (t1, t2) in checked_combinations:
        continue

    # Build query
    params = {
        'level': 'franch', 't1': t1, 't2': t2,
        't3': '--', 't4': '--', 'exclusively': '0'
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to fetch combo {t1}-{t2}: {e}")
        continue

    soup = BeautifulSoup(response.text, 'html.parser')
    table = get_table_from_comments(soup, "results")
    if not table:
        print(f"No results table for combo {t1}-{t2}")
        progress["checked_combinations"].append((t1, t2))
        save_json("progress.json", progress)
        time.sleep(3.2)
        continue

    for row in table.find_all('tr')[1:]:
        link = row.find('a')
        if not link:
            continue
        name = link.text.strip()
        href = link.get('href')
        if name in fetched_players:
            continue
        profile_url = "https://www.pro-football-reference.com" + href

        # Fetch player profile
        try:
            resp = requests.get(profile_url)
            resp.raise_for_status()
        except Exception as e:
            print(f"❌ Failed to fetch {name}: {e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        stats_table = soup.find("table", {"id": "stats"})
        if not stats_table:
            continue

        team_history = set()
        for row in stats_table.find_all("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) < 2:
                continue
            year = cols[0].text.strip()
            team_link = cols[1].find("a")
            if not team_link:
                continue
            team_code = team_link.get("href").split("/")[2]
            team_name = team_map.get(team_code, team_code)
            team_history.add(f"{team_name} ({year})")

        if team_history:
            record = {
                "Player": name,
                "Teams": sorted(team_history)
            }
            print(json.dumps(record, indent=2))
            results.append(record)
            fetched_players.add(name)
            save_json("results.json", results)
            progress["fetched_players"] = list(fetched_players)

        # Wait between player requests
        time.sleep(3.2)

    # Mark this combo as done
    progress["checked_combinations"].append((t1, t2))
    save_json("progress.json", progress)
    time.sleep(3.2)

print("\n✅ Complete. Data saved to 'results.json'.")
print("🔄 Saving progress...")