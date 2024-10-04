import json
import os
import re
import logging
import yt_dlp

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with the URL of the YouTube channel
channel_url = 'https://www.youtube.com/@vintage-archive/videos'  # Ensure this URL is correct

# Path to the JSON file
output_file = 'output/video_details.json'
download_dir = 'downloaded_videos'
starting_label = 1  # Specify the starting label

# Function to extract year from text
def extract_year(text):
    match = re.search(r'\b(19|20)\d{2}\b', text)
    if match:
        return match.group(0)
    return None

# Function to get video URLs using yt-dlp
def get_video_urls(handle_url):
    ydl_opts = {
        'extract_flat': True,
        'force_generic_extractor': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(handle_url, download=False)
        if 'entries' in result:
            return [entry['url'] for entry in result['entries']]
    raise ValueError("Failed to fetch video URLs")

try:
    video_urls = get_video_urls(channel_url)
    logger.info(f"Found {len(video_urls)} videos.")
except Exception as e:
    logger.error(f"Failed to fetch video URLs: {e}")
    raise

# Prepare a list to store video details
videos = []

# Create a directory to save downloaded videos
os.makedirs(download_dir, exist_ok=True)

# Function to fetch video details with retry logic
def fetch_video_details(url, retry=False):
    try:
        with yt_dlp.YoutubeDL() as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get('title', 'No Title')
            description = info_dict.get('description', 'No Description')
            keywords = info_dict.get('tags', [])
            return title, description, keywords
    except Exception as e:
        if not retry:
            logger.warning(f"Retrying for {url} due to error: {e}")
            return fetch_video_details(url, retry=True)
        logger.error(f"Error fetching details for {url} after retry: {e}")
        return None, None, None

# Loop through the video URLs and extract details
for idx, url in enumerate(video_urls, start=1):
    if idx < starting_label:
        continue

    title, description, keywords = fetch_video_details(url)
    if title is None or description is None:
        continue  # Skip this video if fetching details failed

    try:
        # Generate a filename based on the label ID
        download_path = os.path.join(download_dir, f'{idx}.mp4')
        
        # Download the video and save with the label ID as the filename
        ydl_opts = {
            'outtmpl': download_path,
            'format': 'best'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        video_details = {
            'Label': idx,
            'Video URL': url,
            'Title': title,
            'Description': description,
            'Tags': keywords
        }
        videos.append(video_details)
        logger.info(f'Fetched details for video {idx}: {title}')
    except Exception as e:
        logger.error(f'Error downloading video for {url}: {e}')
        continue

# Save the video details to a JSON file in the custom directory
os.makedirs('output', exist_ok=True)

try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=4)
    logger.info(f'Saved details for {len(videos)} videos to {output_file}.')
except Exception as e:
    logger.error(f"Failed to save JSON: {e}")
    raise
