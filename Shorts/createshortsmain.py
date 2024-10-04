import os
import json
import random
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

def resize_clip_for_shorts(clip):
    if clip.duration <= 0:
        print("Warning: Clip has zero duration. Skipping resize.")
        return None
    resized_clip = clip.resize(height=1920)
    print(f"[DEBUG] Resized clip size: {resized_clip.size}")
    
    if resized_clip.w < 1080:
        print(f"Warning: Resized clip width {resized_clip.w} is less than 1080. Skipping crop.")
        return resized_clip
    
    cropped_clip = resized_clip.crop(x_center=resized_clip.w / 2, width=1080)
    print(f"[DEBUG] Cropped clip size: {cropped_clip.size}")
    
    if cropped_clip.w <= 0 or cropped_clip.h <= 0:
        print("Error: Cropped clip has non-positive dimensions. Skipping.")
        return None
    
    return cropped_clip

def add_text_overlay(clip, text, font_path, font_size=120, text_color="orange", stroke_color="black", stroke_width=2):
    if clip is None:
        print("Error: Clip is None in add_text_overlay.")
        return None
    text_img = create_text_image(text, font_path, font_size, text_color, stroke_color, stroke_width)
    if text_img is None:
        print("Error: Text image creation failed. Skipping text overlay.")
        return clip
    if text_img.size[0] == 0 or text_img.size[1] == 0:
        print("Error: Text image has zero size. Skipping text overlay.")
        return clip
    text_clip = ImageClip(np.array(text_img)).set_duration(clip.duration)

    text_clip = text_clip.set_position(('center', 'top'))

    # Ensure text_clip has valid size
    if text_clip.size[0] == 0 or text_clip.size[1] == 0:
        print("Error: Text clip has zero size. Skipping text overlay.")
        return clip

    video = CompositeVideoClip([clip, text_clip])
    print("[DEBUG] Successfully added text overlay.")
    return video

def add_music_overlay(clip, music_source):
    if clip is None:
        print("Error: Clip is None in add_music_overlay.")
        return None
    
    # Check if the music_source is a file or a directory
    if os.path.isfile(music_source):
        music_files = [music_source]  # Use the single file directly
    elif os.path.isdir(music_source):
        music_files = [os.path.join(music_source, f) for f in os.listdir(music_source) if f.endswith(('.mp3', '.wav'))]
    else:
        print(f"Invalid music source: {music_source}. Skipping music overlay.")
        return clip
    
    if not music_files:
        print(f"No music files found in {music_source}. Skipping music overlay.")
        return clip

    # Use the first (and only) file in case of a specific file path
    music_file = music_files[0]
    music_path = music_file

    try:
        audio_clip = AudioFileClip(music_path).subclip(0, clip.duration)
    except Exception as e:
        print(f"Error loading audio file {music_path}: {e}. Skipping music overlay.")
        return clip

    video_with_music = clip.set_audio(audio_clip)
    print(f"[DEBUG] Successfully added music overlay from {music_file}.")
    return video_with_music

def split_video_into_intervals(video_path, output_dir, interval_duration=15, start_index=1, video_map={}, text_overlay=None, font_path=None, music_folder=None):
    try:
        clip = VideoFileClip(video_path)
    except Exception as e:
        print(f"Error loading video file {video_path}: {e}. Skipping.")
        return start_index, video_map
    
    print(f"[DEBUG] Loaded video clip: {video_path}, duration: {clip.duration} seconds, size: {clip.size}")
    
    # Resize the clip to fit YouTube Shorts aspect ratio
    clip = resize_clip_for_shorts(clip)

    if clip is None:
        print(f"Clip from {video_path} is not valid after resizing. Skipping.")
        return start_index, video_map

    print(f"[DEBUG] Clip after resizing/cropping: duration={clip.duration}, size={clip.size}")

    # Define start and end to exclude the first and last 10 seconds
    start_clip = 10
    end_clip = clip.duration - 10

    # Ensure the video is long enough to cut 10 seconds from both ends
    if start_clip >= end_clip:
        print(f"Video {video_path} is too short to cut 10 seconds from both ends.")
        return start_index, video_map

    # Trim the clip
    try:
        trimmed_clip = clip.subclip(start_clip, end_clip)
    except Exception as e:
        print(f"Error trimming video {video_path}: {e}. Skipping.")
        return start_index, video_map

    print(f"[DEBUG] Trimmed clip duration: {trimmed_clip.duration} seconds")

    if trimmed_clip.duration <= 0:
        print(f"Trimmed clip from {video_path} is empty after trimming. Skipping.")
        return start_index, video_map

    # Add text overlay if specified
    if text_overlay and font_path:
        trimmed_clip = add_text_overlay(trimmed_clip, text_overlay, font_path)

    # Add music overlay if specified
    if music_folder:
        trimmed_clip = add_music_overlay(trimmed_clip, music_folder)

    if trimmed_clip is None:
        print(f"Clip from {video_path} became invalid after processing. Skipping.")
        return start_index, video_map

    print(f"[DEBUG] Clip after overlays: duration={trimmed_clip.duration}, size={trimmed_clip.size}")

    # Calculate the number of intervals
    total_duration = trimmed_clip.duration
    num_intervals = int(total_duration // interval_duration)
    
    print(f"[DEBUG] Total duration for interval splitting: {total_duration} seconds, number of intervals: {num_intervals + 1}")

    original_file_name = os.path.basename(video_path)

    for i in range(num_intervals + 1):
        start_time = i * interval_duration
        end_time = start_time + interval_duration

        # Ensure we don't exceed the trimmed video's duration
        if end_time > total_duration:
            end_time = total_duration

        print(f"[DEBUG] Processing interval {i + 1}: {start_time} to {end_time} seconds")

        # Extract the subclip
        try:
            interval_clip = trimmed_clip.subclip(start_time, end_time)
        except Exception as e:
            print(f"Error extracting subclip {start_time}-{end_time} from {video_path}: {e}. Skipping this interval.")
            continue

        if interval_clip.duration <= 0:
            print(f"Interval clip from {video_path} is empty. Skipping this interval.")
            continue

        print(f"[DEBUG] Interval clip duration: {interval_clip.duration} seconds, size: {interval_clip.size}")

        # Generate output file name
        output_file_name = f"{start_index}.mp4"
        output_path = os.path.join(output_dir, output_file_name)
        start_index += 1

        # Use CPU-based encoding
        codec = "libx264"

        # Save the interval clip with CPU acceleration
        try:
            interval_clip.write_videofile(output_path, codec=codec, audio_codec="aac", threads=4, logger=None)
            print(f"Saved: {output_path} (using CPU)")
        except Exception as e:
            print(f"Error saving clip {output_path}: {e}. Skipping this interval.")
            continue

        # Record mapping in the video_map
        video_map[output_file_name] = {"source": original_file_name}

    return start_index, video_map

if __name__ == "__main__":
    # Define the range of videos you want to process
    video_range = range(281, 282)

    # Set the directory containing the original videos
    video_directory = "./Example"

    # Set the directory where the resulting clips will be saved
    output_directory = "./Results"
    os.makedirs(output_directory, exist_ok=True)

    # Path to the font file
    font_path = "./Fonts/Bangers-Regular.ttf"

    # Text to overlay on the video
    text_overlay = "Irish Moments Preserved"

    # Path to the music folder or file
    music_folder = "./Music/irish-jig.mp3"  # Can be a file or a directory

    # Starting index for naming the files
    file_index = 1

    # Dictionary to store mappings
    video_map = {}

    # Process each video file in the defined range
    for video_number in video_range:
        video_file = f"{video_number}.mp4"
        video_path = os.path.join(video_directory, video_file)
        if os.path.exists(video_path):
            print(f"\nProcessing {video_file}...")
            
            # Split the video into intervals, add text and music overlay, and save them in the output directory
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

    # Save the video_map to a JSON file
    json_output_path = os.path.join(output_directory, "video_map.json")
    try:
        with open(json_output_path, "w") as json_file:
            json.dump(video_map, json_file, indent=4)
        print(f"\nVideo mapping saved to {json_output_path}")
    except Exception as e:
        print(f"Error saving video mapping to JSON: {e}")
