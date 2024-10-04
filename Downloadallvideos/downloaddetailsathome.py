import json
import os
import logging
import yt_dlp
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
channel_url = 'https://www.youtube.com/playlist?list=PLttOfW_IF8oudzC4YAqlrHjF2E2_mOX9c'
output_file = 'output/video_details.json'
download_dir = 'M:/Youtube/MovieChannel/'
ffmpeg_location = 'c:/ffmpeg/ffmpeg-master-latest-win64-gpl/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe'

def get_next_file_number():
    existing_files = [f for f in os.listdir(download_dir) if f.endswith('.mp4')]
    return max([int(f.split('.')[0]) for f in existing_files], default=0) + 1

def get_video_urls(handle_url):
    ydl_opts = {'extract_flat': True, 'force_generic_extractor': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(handle_url, download=False)
        return [entry['url'] for entry in result.get('entries', [])]

def fetch_video_details(url, retries=3):
    for attempt in range(retries):
        try:
            with yt_dlp.YoutubeDL() as ydl:
                info_dict = ydl.extract_info(url, download=False)
                return {
                    'title': info_dict.get('title', 'No Title'),
                    'description': info_dict.get('description', 'No Description'),
                    'keywords': info_dict.get('tags', [])
                }
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
    logger.error(f"Failed to fetch details for {url} after {retries} attempts")
    return None

def download_video(url, file_number):
    download_path = os.path.join(download_dir, f'{file_number}.%(ext)s')
    ydl_opts = {
        'outtmpl': download_path,
        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best[ext=mp4]/best',
        'ffmpeg_location': ffmpeg_location,
        'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}],
        'retries': 5,
        'fragment_retries': 5,
        'continuedl': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        logger.error(f"Error downloading video {file_number}: {e}")
        return False

def process_video(url, file_number):
    details = fetch_video_details(url)
    if not details:
        return None

    if download_video(url, file_number):
        return {
            'Label': file_number,
            'Video URL': url,
            'Title': details['title'],
            'Description': details['description'],
            'Tags': details['keywords']
        }
    return None

def main():
    os.makedirs(download_dir, exist_ok=True)
    os.makedirs('output', exist_ok=True)

    try:
        video_urls = get_video_urls(channel_url)
        logger.info(f"Found {len(video_urls)} videos.")
    except Exception as e:
        logger.error(f"Failed to fetch video URLs: {e}")
        return

    file_number = get_next_file_number()
    videos = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(process_video, url, file_number + i): url 
                         for i, url in enumerate(video_urls)}
        
        for future in as_completed(future_to_url):
            result = future.result()
            if result:
                videos.append(result)
                logger.info(f"Successfully processed video: {result['Title']}")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(videos, f, ensure_ascii=False, indent=4)
        logger.info(f'Saved details for {len(videos)} videos to {output_file}.')
    except Exception as e:
        logger.error(f"Failed to save JSON: {e}")

if __name__ == "__main__":
    main()