import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
# Your Twitch Client ID and Access Token
CLIENT_ID = os.getenv("TWITCH_CLIENT")
ACCESS_TOKEN = os.getenv("TWITCH_BEARER")

# IGDB API URL
IGDB_URL = 'https://api.igdb.com/v4/games/'

# Headers for authentication
headers = {
    'Client-ID': CLIENT_ID,
    'Authorization': f'Bearer {ACCESS_TOKEN}',
}


def getTopGames(n=10):
    query = f"""
    fields name, rating, summary, cover.url, first_release_date;
    limit {n};
    sort rating desc;
    where rating_count > 1000;
    """

    response = requests.post(IGDB_URL, headers=headers, data=query)

    # Check for successful response
    if response.status_code == 200:
        games = response.json()
        for game in games:
            print(f"Name: {game['name']}")
            print(f"Rating: {game.get('rating', 'N/A')}")
            release_date = datetime.utcfromtimestamp(
                game['first_release_date']).strftime('%d-%m-%Y')
            print(f"Release Date: {release_date}")
            print(f"Summary: {game.get('summary', 'No summary available.')}")
            print(
                f"Cover URL: {game.get('cover', {}).get('url', 'No cover available.')}")
            print('-' * 40)
    else:
        print(f"Failed to fetch data: {response.status_code}, {response.text}")


getTopGames()
