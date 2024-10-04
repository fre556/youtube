import os
import subprocess
import re

# Manually specify the FFmpeg path here
FFMPEG_PATH = r"C:\ffmpeg\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"

def get_video_duration(input_file):
    """Get the duration of the video using ffmpeg."""
    cmd = [FFMPEG_PATH, '-i', input_file]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    duration = None
    # Look for the duration in the stderr output
    match = re.search(r'Duration: (\d+:\d+:\d+\.\d+)', result.stderr)
    if match:
        duration_str = match.group(1)
        # Convert the duration string to seconds
        h, m, s = map(float, duration_str.split(':'))
        duration = h * 3600 + m * 60 + s
    
    return duration

def cut_first_and_last_5_seconds(video_folder, output_folder, start_label, end_label):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for label in range(start_label, end_label + 1):
        input_file = os.path.join(video_folder, f"{label}.mp4")
        output_file = os.path.join(output_folder, f"{label}_cut.mp4")
        
        if not os.path.isfile(input_file):
            print(f"Video file {input_file} not found, skipping.")
            continue
        
        print(f"Processing video {input_file}...")

        # Get the duration of the video
        duration = get_video_duration(input_file)
        
        if duration is None:
            print(f"Failed to get duration for {input_file}.")
            continue
        
        # Calculate the end time (5 seconds before the end of the video)
        end_time = duration - 5

        # Command to cut the first and last 5 seconds of the video
        cmd = [
            FFMPEG_PATH, 
            '-y',  # Overwrite output file if it exists
            '-i', input_file, 
            '-ss', '5',  # Start 5 seconds into the video
            '-t', str(end_time - 5),  # Duration is end_time minus 5 seconds (for the start offset)
            '-c', 'copy',  # Use stream copy (no re-encode)
            output_file
        ]

        try:
            subprocess.run(cmd, check=True)
            print(f"Saved cut video to {output_file}.")
        except subprocess.CalledProcessError as e:
            print(f"Processing failed for {input_file} with error: {e}")

if __name__ == "__main__":
    video_folder = r"M:\Youtube\Vintage Archive\Videos"  # Path to your video folder
    output_folder = r"M:\Youtube\Vintage Archive\cut"  # Path to save the cut videos
    start_label = int(input("Enter the start label: "))  # Define the start label
    end_label = int(input("Enter the end label: "))  # Define the end label
    
    cut_first_and_last_5_seconds(video_folder, output_folder, start_label, end_label)