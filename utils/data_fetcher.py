"""The purpose of this file is to remove out of sight the technical details
which regard API interaction, in order to increase legibility of other parts
of the program."""

import os
import json
import requests
from dotenv import load_dotenv, find_dotenv
if not find_dotenv():
    print("Error: .env file not found. Consult README.md")
    exit(1)
load_dotenv()

URL_PREFIX = "https://api.themoviedb.org/3/search/movie?query="
URL_SUFFIX = "&language=en-US&page=1"
POSTER_BASE_URL = "https://image.tmdb.org/t/p"
POSTER_IMG_SZ = "/w500"
API_KEY = os.getenv('API_KEY')
SUGGESTIONS_LIMIT = 10


def get_user_selection(movies_list: list):
    """Print the multiple matches found and ask user's choice. If parts of
    data missing, give string placeholders to variables."""
    print("Found multiple matches, which movie do you wish to add?")
    for i, movie in enumerate(movies_list):
        if i == SUGGESTIONS_LIMIT:
            break
        year = movie["release_date"].split("-")[0]
        if not year:
            year = "*release year not found"
        rating = movie["vote_average"]
        if not rating:
            rating = "unavailable"
        elif isinstance(rating, float):
            rating = round(rating, 1)
        elif isinstance(rating, str):
            rating = float(rating[:4])
        print(f"{i + 1}. {movie['title']} ({year}), rating: {rating}")
    while True:
        try:
            choice = int(input("Enter a number: "))
            if choice not in range(1, len(movies_list) + 1):
                print("Error: no movie under that number, try again.")
                continue
            return movies_list[choice - 1]
        except ValueError:
            print("Error: choice must be integer.")


def fetch_data(movie_title: str):
    """Fetches the movie data for 'movie_title'.
    Return: (title, year, rating, poster) of single movie, else None."""
    req_url = URL_PREFIX + movie_title + "&api_key=" + API_KEY + URL_SUFFIX
    try:
        response = requests.get(req_url, timeout=1)
    except requests.ConnectionError:
        print("Error connecting to the internet.")
        return None
    if response.status_code != 200:
        print(f"Error accessing API, status code {response.status_code}")
        return None
    data = response.text
    new_movies_dict = json.loads(data)
    mov_list = new_movies_dict["results"]
    if len(mov_list) == 0:
        print(f"{movie_title} doesn't match any movies.")
        return None
    elif len(mov_list) > 1:
        mov_list[0] = get_user_selection(mov_list)
    if None in (mov_list[0].get("title"), mov_list[0]["release_date"],
                mov_list[0]["vote_average"], mov_list[0]["poster_path"]):
        print("Error fetching data, db incomplete for that entry.")
        return None
    try:  # only meant to catch any errors for int() and round()
        title = mov_list[0]["title"]
        if ',' in title:  # csv precaution: remove any ',' in movie title
            title = title.translate(str.maketrans('', '', ','))
        year = int(mov_list[0]["release_date"].split("-")[0])
        rating = round(mov_list[0]["vote_average"], 1)
        poster = POSTER_BASE_URL + POSTER_IMG_SZ + mov_list[0]["poster_path"]
    except ValueError as e:
        print(e)
        return None
    return title, year, rating, poster
