import json
import requests
import os
import re

API_KEY = "Yfd51ce1509c677dd41ea2ebf4c4617aa"
BASE_URL = "https://api.themoviedb.org/3"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/original"

def clean_title(title):
    # Extract the main title and year
    match = re.match(r"(.*?)\s*(\d{4})\s*(\(.*?\))?\s*(.*)", title)
    if match:
        main_title = match.group(1).strip()
        year = match.group(2)
        return main_title, year
    return title, None

def search_movie(title):
    main_title, year = clean_title(title)
    search_url = f"{BASE_URL}/search/movie"
    params = {
        "api_key": API_KEY,
        "query": main_title,
        "year": year
    }
    response = requests.get(search_url, params=params)
    data = response.json()
    return data.get("results", [])

def download_poster(poster_path, title):
    if not os.path.exists("posters"):
        os.makedirs("posters")
    
    file_name = f"posters/{title.replace(' ', '_').replace(':', '')[:100]}.jpg"
    poster_url = f"{POSTER_BASE_URL}{poster_path}"
    response = requests.get(poster_url)
    
    with open(file_name, "wb") as f:
        f.write(response.content)
    print(f"Downloaded poster for {title}")

def main():
    with open("movies.json", "r", encoding='utf-8') as f:
        movies = json.load(f)
    
    for movie in movies:
        print(f"Processing: {movie['Title']}")
        main_title, year = clean_title(movie['Title'])
        print(f"  Searching for: {main_title} ({year})")
        
        results = search_movie(movie['Title'])
        if results:
            best_match = results[0]
            if best_match.get("poster_path"):
                download_poster(best_match["poster_path"], movie['Title'])
            else:
                print(f"  No poster found for {main_title} ({year}) (TMDB ID: {best_match['id']})")
        else:
            print(f"  No results found for {main_title} ({year})")

if __name__ == "__main__":
    main()