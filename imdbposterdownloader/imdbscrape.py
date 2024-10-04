import json
import requests
from bs4 import BeautifulSoup
import os
import re
import logging
from urllib.parse import quote
import string
from io import BytesIO
from PIL import Image, ImageEnhance

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def clean_title(title):
    # Extract the main title, removing year and additional information
    match = re.match(r"(.*?)(?:\s*\(?\d{4}\)?)?(?:\s*\(.*?\))?\s*(.*)", title)
    if match:
        main_title = match.group(1).strip()
        return main_title
    return title

def extract_year(title):
    year_match = re.search(r'\b(\d{4})\b', title)
    return year_match.group(1) if year_match else None

def search_movie(title, year=None):
    search_url = f"https://www.imdb.com/find?q={quote(title)}&s=tt&ttype=ft&ref_=fn_ft"
    response = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.content, 'html.parser')
    
    results = soup.select('.ipc-metadata-list-summary-item__t')
    
    for result in results:
        result_title = result.text
        result_year_match = re.search(r'\((\d{4})\)', result.find_next('li').text)
        result_year = result_year_match.group(1) if result_year_match else None
        
        if year and result_year == year:
            return "https://www.imdb.com" + result['href']
        elif title.lower() in result_title.lower():
            return "https://www.imdb.com" + result['href']
    
    return None

def get_poster_url(movie_url):
    response = requests.get(movie_url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.content, 'html.parser')
    
    poster = soup.select_one('img.ipc-image')
    if poster and poster.get('src'):
        return poster['src']
    return None

def sanitize_filename(filename):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    sanitized = ''.join(c for c in filename if c in valid_chars)
    return sanitized[:100]  # Limit filename length

def enhance_image(image):
    # Increase sharpness
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.5)  # Increase sharpness by 50%
    
    # Increase contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.2)  # Increase contrast by 20%
    
    return image

def download_and_enhance_poster(poster_url, title):
    if not os.path.exists("posters"):
        try:
            os.makedirs("posters")
        except PermissionError:
            logger.error("Permission denied: Unable to create 'posters' directory.")
            return
    
    sanitized_title = sanitize_filename(title)
    file_name = f"posters/{sanitized_title}.jpg"
    
    try:
        response = requests.get(poster_url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        # Open the image using Pillow
        image = Image.open(BytesIO(response.content))
        
        # Enhance the image
        enhanced_image = enhance_image(image)
        
        # Save the enhanced image
        enhanced_image.save(file_name, "JPEG", quality=95)
        logger.info(f"Downloaded and enhanced poster for {title}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download poster for {title}: {str(e)}")
    except IOError as e:
        logger.error(f"Failed to save poster for {title}: {str(e)}")
    except Exception as e:
        logger.error(f"An error occurred while processing the image for {title}: {str(e)}")

def fallback_search(title):
    # Try searching without the year
    result = search_movie(title)
    if result:
        return result

    # Try searching with each word removed one by one
    words = title.split()
    for i in range(len(words)):
        partial_title = " ".join(words[:i] + words[i+1:])
        result = search_movie(partial_title)
        if result:
            return result

    return None

def main():
    try:
        with open("movies.json", "r", encoding='utf-8') as f:
            movies = json.load(f)
    except IOError as e:
        logger.error(f"Failed to open movies.json: {str(e)}")
        return
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse movies.json: {str(e)}")
        return
    
    for movie in movies:
        logger.info(f"Processing: {movie['Title']}")
        main_title = clean_title(movie['Title'])
        year = extract_year(movie['Title'])
        logger.info(f"  Cleaned title: {main_title}")
        if year:
            logger.info(f"  Year: {year}")
        
        try:
            movie_url = search_movie(main_title)
            if not movie_url and year:
                logger.info(f"  No results found. Trying with year...")
                movie_url = search_movie(f"{main_title} {year}")
            if not movie_url:
                logger.info(f"  Still no results. Trying fallback search...")
                movie_url = fallback_search(main_title)
            
            if movie_url:
                logger.info(f"  Movie found: {movie_url}")
                poster_url = get_poster_url(movie_url)
                if poster_url:
                    download_and_enhance_poster(poster_url, movie['Title'])
                else:
                    logger.info(f"  No poster found for the movie.")
            else:
                logger.info(f"  No results found for {main_title}")
        except Exception as e:
            logger.error(f"An error occurred while processing {movie['Title']}: {str(e)}")
        
        logger.info("") # Empty line for readability

if __name__ == "__main__":
    main()
    