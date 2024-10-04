import os
import json
import subprocess
import numpy as np
from moviepy.editor import VideoFileClip, CompositeVideoClip, AudioFileClip, ImageClip
from PIL import Image, ImageDraw, ImageFont

# Monkey-patch Image.ANTIALIAS to Image.LANCZOS in case moviepy uses it.
Image.ANTIALIAS = Image.LANCZOS

def create_text_image(text, font_path, font_size, text_color="orange", stroke_color="black", stroke_width=2):
    try:
        font = ImageFont.truetype(font_path, font_size)
    except OSError:
        print("Failed to load the specified font. Falling back to the default font.")
        font = ImageFont.load_default()

    dummy_img = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    text_bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    print(f"[DEBUG] Text bounding box size: width={text_width}, height={text_height}")

    if text_width <= 0 or text_height <= 0:
        print("Error: Text bounding box has non-positive dimensions.")
        return None

    img = Image.new("RGBA", (text_width, text_height), (255, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.text((-text_bbox[0], -text_bbox[1]), text, font=font, fill=text_color, stroke_width=stroke_width, stroke_fill=stroke_color)

    print(f"[DEBUG] Created text image size: {img.size}")
    return img

def process_with_opencl_ffmpeg(input_path, output_path):
    """Pre-process video with OpenCL-accelerated FFmpeg."""
    ffmpeg_path = r'C:\ffmpeg\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe'  # Update with your actual path
    command = [
        ffmpeg_path,
        '-init_hw_device', 'opencl=gpu:0',  # Initialize OpenCL device
        '-filter_hw_device', 'gpu',
        '-i', input_path,  # Input file
        '-vf', 'scale=1080:1920:flags=bicubic',  # Using standard scaling instead of OpenCL due to errors
        '-c:v', 'h264_nvenc',  # Use NVENC for encoding (still uses GPU for encoding)
        output_path  # Output file
    ]
    try:
        subprocess.run(command, check=True)
        print(f"[INFO] OpenCL-accelerated processing complete: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] FFmpeg OpenCL processing failed: {e}")
        return False
    return True

def add_text_overlay(clip, text, font_path, font_size=120, text_color="orange", stroke_color="black", stroke_width=2):
    text_img = create_text_image(text, font_path, font_size, text_color, stroke_color, stroke_width)
    if text_img is None:
        return clip

    text_clip = ImageClip(np.array(text_img)).set_duration(clip.duration)
    text_clip = text_clip.set_position(('center', 'top'))

    return CompositeVideoClip([clip, text_clip])

def add_music_overlay(clip, music_source):
    if os.path.isfile(music_source):
        music_files = [music_source]
    elif os.path.isdir(music_source):
        music_files = [os.path.join(music_source, f) for f in os.listdir(music_source) if f.endswith(('.mp3', '.wav'))]
    else:
        return clip
    
    if not music_files:
        return clip

    music_path = music_files[0]
    try:
        audio_clip = AudioFileClip(music_path).subclip(0, clip.duration)
    except Exception as e:
        return clip

    return clip.set_audio(audio_clip)

def split_video_into_intervals(video_path, output_dir, interval_duration=15, start_index=1, video_map={}, text_overlay=None, font_path=None, music_folder=None):
    resized_output_path = os.path.join(output_dir, "resized_temp.mp4")
    
    # Resize video using OpenCL
    if not process_with_opencl_ffmpeg(video_path, resized_output_path):
        print(f"[ERROR] OpenCL processing failed for {video_path}. Skipping.")
        return start_index, video_map
    
    try:
        clip = VideoFileClip(resized_output_path)
    except Exception as e:
        print(f"Error loading video file {resized_output_path}: {e}. Skipping.")
        return start_index, video_map

    # Define start and end to exclude the first and last 10 seconds
    start_clip = 10
    end_clip = clip.duration - 10

    # Trim the clip
    trimmed_clip = clip.subclip(start_clip, end_clip)

    # Add text overlay if specified
    if text_overlay and font_path:
        trimmed_clip = add_text_overlay(trimmed_clip, text_overlay, font_path)

    # Add music overlay if specified
    if music_folder:
        trimmed_clip = add_music_overlay(trimmed_clip, music_folder)

    # Calculate the number of intervals
    total_duration = trimmed_clip.duration
    num_intervals = int(total_duration // interval_duration)

    original_file_name = os.path.basename(video_path)

    for i in range(num_intervals + 1):
        start_time = i * interval_duration
        end_time = start_time + interval_duration

        if end_time > total_duration:
            end_time = total_duration

        interval_clip = trimmed_clip.subclip(start_time, end_time)

        output_file_name = f"{start_index}.mp4"
        output_path = os.path.join(output_dir, output_file_name)
        start_index += 1

        interval_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", threads=4, logger=None)
        video_map[output_file_name] = {"source": original_file_name}

    return start_index, video_map

if __name__ == "__main__":
    video_range = range(281, 282)
    video_directory = "./Example"
    output_directory = "./Results"
    os.makedirs(output_directory, exist_ok=True)

    font_path = "./Fonts/Bangers-Regular.ttf"
    text_overlay = "Test"
    music_folder = "./Music/irish-jig.mp3"

    file_index = 1
    video_map = {}

    for video_number in video_range:
        video_file = f"{video_number}.mp4"
        video_path = os.path.join(video_directory, video_file)
        if os.path.exists(video_path):
            print(f"\nProcessing {video_file}...")
            file_index, video_map = split_video_into_intervals(
                video_path, 
                output_directory, 
                interval_duration=15, 
                start_index=file_index, 
                video_map=video_map, 
                text_overlay=text_overlay, 
                font_path=font_path,
                music_folder=music_folder
            )
        else:
            print(f"Video {video_file} does not exist in the directory.")

    json_output_path = os.path.join(output_directory, "video_map.json")
    with open(json_output_path, "w") as json_file:
        json.dump(video_map, json_file, indent=4)
    print(f"\nVideo mapping saved to {json_output_path}")
