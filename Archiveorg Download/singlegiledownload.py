import os
import json
import logging
import requests
from internetarchive import get_item

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directories to save the video details JSON file and downloaded videos
output_dir = 'output'
video_dir = 'downloaded_videos'
output_file = 'single_video_details.json'

# Video identifier on archive.org
video_identifier = 'match_your_mood'

# Set the starting label number
start_label = 30

def download_video(video_url, label):
    try:
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        video_path = os.path.join(video_dir, f"{label}.mp4")
        with open(video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"Downloaded video {label} from {video_url}")
        return video_path
    except Exception as e:
        logger.error(f"Failed to download video {label}: {e}")
        return None

def main():
    # Create directories to save the JSON file and videos
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(video_dir, exist_ok=True)
    
    # Fetch the item metadata
    item = get_item(video_identifier)
    
    # Print metadata for debugging
    for k, v in item.metadata.items():
        logger.debug(f"{k}: {v}")

    # Use the provided start label
    label = start_label

    # Gather video details
    video_details_list = []
    video_details = {
        'Label': label,
        'Identifier': video_identifier,
        'Title': item.metadata.get('title', 'No Title'),
        'Description': item.metadata.get('description', 'No Description'),
        'Tags': item.metadata.get('subject', []),
        'Video URL': f"https://archive.org/download/{video_identifier}/{video_identifier}.mp4",  # Assuming .mp4 format
        'Reviews': item.reviews if hasattr(item, 'reviews') else []
    }
    video_details_list.append(video_details)
    logger.info(f"Fetched details for video {video_identifier}: {video_details['Title']}")

    # Download the video
    video_url = video_details['Video URL']
    downloaded_path = download_video(video_url, label)
    if downloaded_path:
        video_details['Downloaded Path'] = downloaded_path

    # Save the video details to a JSON file
    output_path = os.path.join(output_dir, output_file)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(video_details_list, f, ensure_ascii=False, indent=4)
        logger.info(f'Saved details for the video to {output_path}.')
    except Exception as e:
        logger.error(f"Failed to save JSON: {e}")
        raise

if __name__ == '__main__':
    main()
