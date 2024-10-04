import os
import json
import requests
from tqdm import tqdm

# JSON file with video metadata
json_file = 'output/collection_video_details.json'

# Directory to save downloaded videos
download_dir = 'C:/Users/mini-beast/Videos/Project'
os.makedirs(download_dir, exist_ok=True)

# Define start and end labels as integers for easy modification
start_label = 12541
end_label = 12565  # Set your end label here

def get_smallest_video_url(item_identifier):
    item_metadata_url = f"https://archive.org/metadata/{item_identifier}"
    response = requests.get(item_metadata_url)
    if response.status_code != 200:
        return None
    data = response.json()
    files = data.get('files', [])
    video_files = [file for file in files if file['name'].endswith('.mp4')]
    if not video_files:
        return None
    # Sort video files by size and get the smallest one
    video_files.sort(key=lambda x: int(x.get('size', float('inf'))))
    return f"https://archive.org/download/{item_identifier}/{video_files[0]['name']}"

def download_video(url, filename):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    chunk_size = 1024  # 1 KB
    with open(filename, 'wb') as file, tqdm(
        desc=filename,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=chunk_size):
            file.write(chunk)
            bar.update(len(chunk))

def main(start_label, end_label):
    with open(json_file, 'r', encoding='utf-8') as f:
        video_details_list = json.load(f)

    for video_details in video_details_list:
        label = video_details['Label']
        if start_label <= label <= end_label:
            item_identifier = video_details['Identifier']
            video_url = get_smallest_video_url(item_identifier)
            if video_url:
                filename = os.path.join(download_dir, f'{label}.mp4')
                try:
                    download_video(video_url, filename)
                    print(f"Downloaded video {label} from {video_url}")
                except Exception as e:
                    print(f"Failed to download video {label} from {video_url}: {e}")
            else:
                print(f"No suitable video file found for video {label} at https://archive.org/download/{item_identifier}")

if __name__ == '__main__':
    main(start_label, end_label)
