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

            if 'cover' in game:
                cover_url = game['cover'].get(
                    'url', 'No cover available.')[2:].replace("thumb", "cover_big")
            else:
                cover_url = ''

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


def getGameById(id):
    # offset is for pagination -> basically top n games from [offset,n+offset]
    query = f"""
    fields name, cover.url, artworks.url, rating, genres.name, storyline;
    where id = {id};
    """
    response = requests.post(IGDB_URL, headers=headers, data=query)

    if response.status_code == 200:
        game = response.json()[0]
        formattedData = []

        if 'cover' in game:
            cover_url = game['cover'].get(
                'url', 'No cover available.')[2:].replace("thumb", "cover_big")
        else:
            cover_url = ''

        if 'artworks' in game:
            artwork_url = game['artworks'][0].get(
                'url', 'No cover available.').replace("thumb", "1080p")
        else:
            artwork_url = ''

        formattedData.append({
            "id": game["id"],
            "name": game["name"],
            "rating": round(game.get("rating", 0), 1),
            "genre": game["genres"][0]["name"] if "genres" in game and game["genres"] else "N/A",
            "cover": f"https:{cover_url}" if cover_url else "No Image",
            "artwork": f"https:{artwork_url}" if artwork_url else "No Image"
        })
        return formattedData[0]

    else:
        return


def searchGame(searchData):
    # offset is for pagination -> basically top n games from [offset,n+offset]
    print(searchData)
    query = f'''
    fields id, name, cover.url, rating, genres.name;
    where name ~ "{str(searchData)}"*;
    sort rating desc; 
    limit 15;
    '''
    response = requests.post(IGDB_URL, headers=headers, data=query)

    if response.status_code == 200:
        games = response.json()
        formattedData = []
        for game in games:
            """
            Structure of data is like: game[''] - name,rating,genre, cover{'url':...}, 
            """

            if 'cover' in game:
                cover_url = game['cover'].get(
                    'url', 'No cover available.')[2:].replace("thumb", "cover_big")
            else:
                cover_url = ''

            formattedData.append({
                "id": game["id"],
                "name": game["name"],
                "rating": round(game.get("rating", 0), 1),
                "genre": game["genres"][0]["name"] if "genres" in game and game["genres"] else "N/A",
                "cover": f"https:{cover_url}" if cover_url else "No Image"
            })
        return formattedData
    else:
        print(response)
        return []

# release_date = datetime.utcfromtimestamp(
# game['first_release_date']).strftime('%d-%m-%Y')
# print(f"Release Date: {release_date}")
# print(f"Summary: {game.get('summary', 'No summary available.')}")

# artwork_full_size = game['artworks'][0].get(
# 'url', 'No cover available.')[2:].replace("thumb", "1080p")
