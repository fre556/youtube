import os
import json
import subprocess
import numpy as np
import random
import yaml
import multiprocessing as mp
from moviepy.editor import VideoFileClip, CompositeVideoClip, AudioFileClip, ImageClip, vfx
from PIL import Image, ImageDraw, ImageFont
import logging

# Monkey-patch Image.ANTIALIAS to Image.LANCZOS in case moviepy uses it.
Image.ANTIALIAS = Image.LANCZOS

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration from a YAML file
def load_config(config_path):
    logging.info(f"Loading configuration from {config_path}")
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def create_text_image(text, font_path, font_size, text_color="orange", stroke_color="black", stroke_width=2, debug=False):
    logging.info("Creating text image")
    try:
        font = ImageFont.truetype(font_path, font_size)
    except OSError:
        logging.warning("Failed to load the specified font. Falling back to the default font.")
        font = ImageFont.load_default()

    dummy_img = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    text_bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    if debug:
        logging.debug(f"Text bounding box size: width={text_width}, height={text_height}")

    if text_width <= 0 or text_height <= 0:
        logging.error("Text bounding box has non-positive dimensions.")
        return None

    img = Image.new("RGBA", (text_width, text_height), (255, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.text((-text_bbox[0], -text_bbox[1]), text, font=font, fill=text_color, stroke_width=stroke_width, stroke_fill=stroke_color)

    if debug:
        logging.debug(f"Created text image size: {img.size}")
    return img

def process_with_opencl_ffmpeg(input_path, output_path, config, debug=False):
    logging.info(f"Processing video with OpenCL FFmpeg: {input_path} -> {output_path}")
    ffmpeg_path = config['ffmpeg_path']

    # Ensure the FFmpeg path exists
    if not os.path.isfile(ffmpeg_path):
        logging.error(f"FFmpeg path not found: {ffmpeg_path}")
        raise FileNotFoundError(f"FFmpeg path not found: {ffmpeg_path}")

    command = [
        ffmpeg_path,
        '-init_hw_device', 'opencl=gpu:0',  # Initialize OpenCL device
        '-filter_hw_device', 'gpu',
        '-i', input_path,  # Input file
        '-vf', 'scale=1080:1920:flags=bicubic',  # Using standard scaling instead of OpenCL due to errors
        '-c:v', 'h264_nvenc',  # Use NVENC for encoding (still uses GPU for encoding)
        '-preset', 'fast',  # Speed up the encoding process
        output_path  # Output file
    ]
    if debug:
        logging.debug(f"Running command: {' '.join(command)}")
    
    try:
        subprocess.run(command, check=True)
        logging.info(f"OpenCL-accelerated processing complete: {output_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"FFmpeg OpenCL processing failed: {e}")
        return False
    return True

def enhance_video(clip, debug=False):
    logging.info("Enhancing video with color and contrast adjustments.")
    clip = clip.fx(vfx.colorx, 1.02)  # Boost color by 2%
    clip = clip.fx(vfx.lum_contrast, contrast=1.05)  # Increase contrast by 5%
    clip = clip.fx(vfx.lum_contrast, lum=1.05)  # Slight brightness increase
    clip = clip.fx(vfx.lum_contrast, contrast=1.05, contrast_thr=105)  # Sharpening effect
    
    if debug:
        logging.debug("Enhanced video with color and contrast adjustments.")
    
    return clip

def add_text_overlay(clip, text, font_path, font_size=120, text_color="orange", stroke_color="black", stroke_width=2, text_position=('center', 'top'), debug=False):
    logging.info(f"Adding text overlay: {text}")
    text_img = create_text_image(text, font_path, font_size, text_color, stroke_color, stroke_width, debug)
    if text_img is None:
        return clip

    text_clip = ImageClip(np.array(text_img)).set_duration(clip.duration)
    text_clip = text_clip.set_position(text_position)

    if debug:
        logging.debug(f"Added text overlay at position: {text_position}")

    return CompositeVideoClip([clip, text_clip])

def add_music_overlay(clip, music_source, debug=False):
    logging.info(f"Adding music overlay from source: {music_source}")
    if os.path.isfile(music_source):
        music_files = [music_source]
    elif os.path.isdir(music_source):
        music_files = [os.path.join(music_source, f) for f in os.listdir(music_source) if f.endswith(('.mp3', '.wav'))]
    else:
        return clip
    
    if not music_files:
        return clip

    music_path = random.choice(music_files)
    
    if debug:
        logging.debug(f"Selected music file: {music_path}")

    try:
        audio_clip = AudioFileClip(music_path).subclip(0, clip.duration)
    except Exception as e:
        if debug:
            logging.error(f"Failed to load music file: {e}")
        return clip

    return clip.set_audio(audio_clip)

def process_video_interval(video_data):
    video_path, output_dir, config, debug, start_index = video_data
    logging.info(f"Processing video: {video_path}")
    video_id = os.path.splitext(os.path.basename(video_path))[0]
    resized_output_path = os.path.join(output_dir, f"{video_id}_resized.mp4")
    
    # Resize video using OpenCL
    if not process_with_opencl_ffmpeg(video_path, resized_output_path, config, debug):
        logging.error(f"OpenCL processing failed for {video_path}. Skipping.")
        return None
    
    try:
        clip = VideoFileClip(resized_output_path)
    except Exception as e:
        logging.error(f"Error loading video file {resized_output_path}: {e}. Skipping.")
        return None

    # Enhance the video
    clip = enhance_video(clip, debug)

    # Define start and end to exclude the first and last 10 seconds
    start_clip = 10
    end_clip = clip.duration - 10

    # Trim the clip
    trimmed_clip = clip.subclip(start_clip, end_clip)

    # Add text overlay if specified
    if config['text_overlay'] and config['font_path']:
        trimmed_clip = add_text_overlay(
            trimmed_clip, 
            config['text_overlay'], 
            config['font_path'], 
            text_position=config['text_position'],
            debug=debug
        )

    # Add music overlay if specified
    if config['music_folder']:
        trimmed_clip = add_music_overlay(trimmed_clip, config['music_folder'], debug)

    # Calculate the number of intervals
    total_duration = trimmed_clip.duration
    num_intervals = int(total_duration // config['interval_duration'])

    original_file_name = os.path.basename(video_path)
    interval_map = {}

    for i in range(num_intervals + 1):
        start_time = i * config['interval_duration']
        end_time = start_time + config['interval_duration']

        if end_time > total_duration:
            end_time = total_duration

        interval_clip = trimmed_clip.subclip(start_time, end_time)

        output_file_name = f"{start_index}.mp4"  # Use start_index to name the file
        output_path = os.path.join(output_dir, output_file_name)

        logging.info(f"Saving interval clip: {output_file_name}")
        # Specify the 1 Mbps bitrate for YouTube Shorts
        interval_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", bitrate="1000k", threads=2, logger=None)
        interval_map[output_file_name] = {"source": original_file_name}
        start_index += 1  # Increment start_index for the next file

    clip.close()  # Ensure resources are freed
    return interval_map, start_index

def split_video_into_intervals(video_path, output_dir, config, video_map={}, debug=False, start_index=1):
    logging.info(f"Splitting video into intervals: {video_path}")
    video_data = (video_path, output_dir, config, debug, start_index)
    interval_map, start_index = process_video_interval(video_data)

    if interval_map:
        video_map.update(interval_map)

    return video_map, start_index

def process_all_videos_in_parallel(video_paths, output_dir, config, debug=False, start_index=1):
    logging.info("Processing all videos in parallel")
    with mp.Pool(mp.cpu_count()) as pool:
        results = [pool.apply_async(process_video_interval, ((video_path, output_dir, config, debug, start_index),)) for video_path in video_paths]

        video_map = {}
        for result in results:
            interval_map, start_index = result.get()
            if interval_map:
                video_map.update(interval_map)

    return video_map

if __name__ == "__main__":
    logging.info("Starting video processing")
    # Load the configuration file
    config_path = "config.yaml"
    config = load_config(config_path)
    
    debug = config.get('debug', False)
    video_range = config['video_range']
    video_directory = config['video_directory']
    output_directory = config['output_directory']
    start_index = config.get('start_index', 1)  # Default start_index to 1
    os.makedirs(output_directory, exist_ok=True)

    logging.info(f"Video range: {video_range}")
    logging.info(f"Video directory: {video_directory}")
    logging.info(f"Output directory: {output_directory}")
    logging.info(f"Starting index for file names: {start_index}")

    # Gather all video paths based on the provided range
    video_paths = [os.path.join(video_directory, f"{video_number}.mp4") for video_number in video_range]

    logging.info(f"Processing {len(video_paths)} videos")

    # Process all videos in parallel
    video_map = process_all_videos_in_parallel(video_paths, output_directory, config, debug=debug, start_index=start_index)

    json_output_path = os.path.join(output_directory, "video_map.json")
    with open(json_output_path, "w") as json_file:
        json.dump(video_map, json_file, indent=4)
    logging.info(f"Video mapping saved to {json_output_path}")
