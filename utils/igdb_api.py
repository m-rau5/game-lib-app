import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

CLIENT_ID = os.getenv("TWITCH_CLIENT")
ACCESS_TOKEN = os.getenv("TWITCH_BEARER")
IGDB_URL = 'https://api.igdb.com/v4/games/'

# headers for authentication
headers = {
    'Client-ID': CLIENT_ID,
    'Authorization': f'Bearer {ACCESS_TOKEN}',
}


def getTopGames(n=10, offset=0):
    # offset is for pagination -> basically top n games from [offset,n+offset]
    query = f"""
    fields id, name, cover.url, rating, genres.name;
    limit {n};
    offset {offset};
    sort rating desc;
    where rating_count > 1000;
    """

    response = requests.post(IGDB_URL, headers=headers, data=query)

    if response.status_code == 200:
        games = response.json()
        formattedData = []
        for game in games:
            """
            Structure of data is like: game[''] - name,rating,genre, cover{'url':...}, 
            """
            cover_url = game['cover'].get(
                'url', 'No cover available.')[2:].replace("thumb", "cover_big")

            formattedData.append({
                "id": game["id"],
                "name": game["name"],
                "rating": round(game.get("rating", 0), 1),
                "genre": game["genres"][0]["name"] if "genres" in game and game["genres"] else "N/A",
                "cover": f"https:{cover_url}" if cover_url else "No Image"
            })

            # REMEMBER TO CHANGE t_thumb to: t_1080p OR t_cover_small/big !!!!!!!!

        return formattedData
    else:
        return []


# release_date = datetime.utcfromtimestamp(
# game['first_release_date']).strftime('%d-%m-%Y')
# print(f"Release Date: {release_date}")
# print(f"Summary: {game.get('summary', 'No summary available.')}")

# artwork_full_size = game['artworks'][0].get(
# 'url', 'No cover available.')[2:].replace("thumb", "1080p")
