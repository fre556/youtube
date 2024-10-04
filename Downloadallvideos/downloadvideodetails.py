import json
import os
import logging
import yt_dlp

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with the URL of the YouTube channel or playlist
channel_url = 'https://www.youtube.com/playlist?list=PLttOfW_IF8oudzC4YAqlrHjF2E2_mOX9c'  # Ensure this URL is correct

# Path to the JSON file
output_file = 'output/video_details.json'
download_dir = 'M:/Youtube/MovieChannel'

# Path to your ffmpeg binary
ffmpeg_location = 'c:/ffmpeg/ffmpeg-master-latest-win64-gpl/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe'  # Replace with your actual path

# Function to get the next available file number
def get_next_file_number():
    existing_files = [f for f in os.listdir(download_dir) if f.endswith('.mp4')]
    if not existing_files:
        return 1
    max_number = max([int(f.split('.')[0]) for f in existing_files])
    return max_number + 1

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

# Get the starting file number
file_number = get_next_file_number()

# Loop through the video URLs and extract details
for url in video_urls:
    title, description, keywords = fetch_video_details(url)
    if not title or not description:
        continue  # Skip this video if fetching details failed

    try:
        # Generate a filename based on the next available number
        download_path = os.path.join(download_dir, f'{file_number}.%(ext)s')
        
        # Download the video and save with the sequential number as the filename
        ydl_opts = {
            'outtmpl': download_path,
            'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best[ext=mp4]/best',
            'ffmpeg_location': ffmpeg_location,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        video_details = {
            'Label': file_number,
            'Video URL': url,
            'Title': title,
            'Description': description,
            'Tags': keywords
        }
        videos.append(video_details)
        logger.info(f'Downloaded video {file_number}: {title}')
        
        # Increment the file number for the next video
        file_number += 1
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