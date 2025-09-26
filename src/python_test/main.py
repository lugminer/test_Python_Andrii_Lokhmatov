import pandas as pd
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get API key from environment variable
headers = {
    "X-Auth-Token": os.getenv("X_AUTH_TOKEN")
}
COMPETITION = "PL"  # Premier League
SEASONS = [2023, 2024, 2025]
BASE_URL = "https://api.football-data.org/v4"

all_rows = []

for year in SEASONS:
    # --- 1. Get list of teams in the season ---
    url = f"{BASE_URL}/competitions/{COMPETITION}/teams"
    params = {"season": year}
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        print(f"Error {resp.status_code} for season {year}: {resp.text}")
        continue
    data = resp.json()

    # Initialize dictionary for statistics
    stats = {
        team["id"]: {
            "season": year,
            "team_id": team.get("id"),
            "name": team.get("name"),
            "shortName": team.get("shortName"),
            "tla": team.get("tla"),
            "crestUrl": team.get("crest"),
            "address": team.get("address"),
            "founded": team.get("founded"),
            "games_played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_for": 0,
            "goals_against": 0,
        }
        for team in data.get("teams", [])
    }

    # --- 2. Get season matches ---
    url_matches = f"{BASE_URL}/competitions/{COMPETITION}/matches"
    params = {"season": year}
    resp_matches = requests.get(url_matches, headers=headers, params=params)
    if resp_matches.status_code != 200:
        print(f"Error {resp_matches.status_code} for matches {year}: {resp_matches.text}")
        continue
    matches = resp_matches.json().get("matches", [])

    for m in matches:
        home_id = m["homeTeam"]["id"]
        away_id = m["awayTeam"]["id"]
        score_home = m["score"]["fullTime"]["home"]
        score_away = m["score"]["fullTime"]["away"]

        # if match hasn't been played yet
        if score_home is None or score_away is None:
            continue

        # update statistics for home team
        if home_id in stats:
            t = stats[home_id]
            t["games_played"] += 1
            t["goals_for"] += score_home
            t["goals_against"] += score_away
            if score_home > score_away:
                t["wins"] += 1
            elif score_home == score_away:
                t["draws"] += 1
            else:
                t["losses"] += 1

        # update statistics for away team
        if away_id in stats:
            t = stats[away_id]
            t["games_played"] += 1
            t["goals_for"] += score_away
            t["goals_against"] += score_home
            if score_away > score_home:
                t["wins"] += 1
            elif score_home == score_away:
                t["draws"] += 1
            else:
                t["losses"] += 1

    all_rows.extend(stats.values())

# --- 3. Save the results ---
df = pd.DataFrame(all_rows)
df.to_csv("pl_teams_with_stats.csv", index=False)

print("Saved: pl_teams_with_stats.csv")