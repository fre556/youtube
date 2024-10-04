import os
import subprocess
import re

def get_video_duration(ffmpeg_path, input_file):
    """Get the duration of the video using ffmpeg."""
    cmd = [ffmpeg_path, '-i', input_file]
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
    
    ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg', 'bin', 'ffmpeg.exe')
    
    for label in range(start_label, end_label + 1):
        input_file = os.path.join(video_folder, f"{label}.mp4")
        output_file = os.path.join(output_folder, f"{label}_cut.mp4")
        
        if not os.path.isfile(input_file):
            print(f"Video file {input_file} not found, skipping.")
            continue
        
        print(f"Processing video {input_file}...")

        # Get the duration of the video
        duration = get_video_duration(ffmpeg_path, input_file)
        
        if duration is None:
            print(f"Failed to get duration for {input_file}.")
            continue
        
        # Calculate the duration to keep
        duration_to_keep = duration - 10  # remove 5 seconds from start and 5 seconds from end

        # Command to cut the first and last 5 seconds of the video
        cmd = [
            ffmpeg_path, '-y', '-i', input_file, '-ss', '5', '-t', str(duration_to_keep), '-c', 'copy', output_file
        ]

        try:
            subprocess.run(cmd, check=True)
            print(f"Saved cut video to {output_file}.")
        except subprocess.CalledProcessError as e:
            print(f"Processing failed for {input_file} with error: {e}")

if __name__ == "__main__":
    video_folder = "videos"  # Path to your video folder
    output_folder = "output_videos"  # Path to save the cut videos
    start_label = int(input("Enter the start label: "))  # Define the start label
    end_label = int(input("Enter the end label: "))  # Define the end label
    
    cut_first_and_last_5_seconds(video_folder, output_folder, start_label, end_label)
