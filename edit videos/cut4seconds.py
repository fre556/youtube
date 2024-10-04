import os
import subprocess

def cut_first_5_seconds_and_add_watermark(video_folder, output_folder, watermark_path, start_label, end_label):
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

        # Resize the watermark
        resized_watermark = os.path.join(output_folder, "resized_watermark.png")
        resize_cmd = [
            ffmpeg_path, '-y', '-i', watermark_path, '-vf', 'scale=32:24', resized_watermark
        ]

        try:
            subprocess.run(resize_cmd, check=True)
            print(f"Resized watermark saved to {resized_watermark}.")
        except subprocess.CalledProcessError as e:
            print(f"Watermark resizing failed with error: {e}")
            continue
        
        # Command to cut the video and add the watermark with transparency
        cmd = [
            ffmpeg_path, '-y', '-i', input_file, '-i', resized_watermark,
            '-filter_complex', '[0:v]trim=start=5,setpts=PTS-STARTPTS[v0];[v0][1:v]overlay=W-w-10:H-h-10:format=auto, colorchannelmixer=aa=0.3',
            '-c:v', 'libx264', '-preset', 'fast', '-c:a', 'copy', output_file
        ]

        try:
            subprocess.run(cmd, check=True)
            print(f"Saved cut and watermarked video to {output_file}.")
        except subprocess.CalledProcessError as e:
            print(f"Processing failed for {input_file} with error: {e}")

if __name__ == "__main__":
    video_folder = "videos"  # Path to your video folder
    output_folder = "output_videos"  # Path to save the cut videos
    watermark_path = "watermark.jpg"  # Path to your watermark image
    start_label = int(input("Enter the start label: "))  # Define the start label
    end_label = int(input("Enter the end label: "))  # Define the end label
    
    cut_first_5_seconds_and_add_watermark(video_folder, output_folder, watermark_path, start_label, end_label)
