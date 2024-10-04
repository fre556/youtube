import os
import json
import logging
from internetarchive import search_items, get_item

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directories to save the video details JSON file
output_dir = 'output'
output_file = 'collection_video_details.json'

# Collection identifier on archive.org
collection_identifier = 'prelinger'  # Example collection; replace with your actual collection

# Set the starting label number
start_label = 2993

def fetch_metadata(item_identifier, label):
    try:
        item = get_item(item_identifier)
        
        # Find the correct video URL
        video_url = None
        for file in item.files:
            if file.get('format') in ['h.264', 'MPEG4', '512Kb MPEG4', 'Ogg Video', 'HiRes MPEG4']:
                video_url = f"https://archive.org/download/{item_identifier}/{file['name']}"
                break
        
        # Handle variations in the video file names
        if not video_url:
            for file in item.files:
                if '3mb' in file['name'] and file.get('format') in ['h.264', 'MPEG4', '512Kb MPEG4', 'Ogg Video', 'HiRes MPEG4']:
                    video_url = f"https://archive.org/download/{item_identifier}/{file['name']}"
                    break
        
        video_details = {
            'Label': label,
            'Identifier': item_identifier,
            'Title': item.metadata.get('title', 'No Title'),
            'Description': item.metadata.get('description', 'No Description'),
            'Tags': item.metadata.get('subject', []),
            'Video URL': video_url if video_url else 'No Video URL Found',
            'Reviews': item.reviews if hasattr(item, 'reviews') else []
        }
        
        logger.info(f"Fetched details for video {item_identifier}: {video_details['Title']}")
        return video_details
    except Exception as e:
        logger.error(f"Failed to fetch metadata for {item_identifier}: {e}")
        return None

def main():
    # Create directory to save the JSON file
    os.makedirs(output_dir, exist_ok=True)
    
    # Fetch metadata for each item in the collection
    video_details_list = []
    label = start_label

    # Use search_items with pagination
    search_results = search_items(f'collection:{collection_identifier} AND mediatype:movies')

    for result in search_results:
        item_identifier = result['identifier']
        video_details = fetch_metadata(item_identifier, label)
        if video_details:
            video_details_list.append(video_details)
            label += 1  # Increment the label for the next video

    # Save the combined JSON file
    output_path = os.path.join(output_dir, output_file)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(video_details_list, f, ensure_ascii=False, indent=4)
        logger.info(f'Saved combined details for all videos to {output_path}.')
    except Exception as e:
        logger.error(f"Failed to save combined JSON: {e}")
        raise

if __name__ == '__main__':
    main()
