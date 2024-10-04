import os
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps
import numpy as np

def capture_screenshot(video_path, time=20):
    print(f"Capturing screenshot from {video_path} at {time} seconds.")
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_number = int(fps * time)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    success, frame = cap.read()
    if success:
        print("Screenshot captured successfully.")
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    else:
        print("Failed to capture screenshot.")
        return None

def enhance_image(image):
    print("Enhancing image.")
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.5)  # Increase contrast
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.5)  # Increase sharpness
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.0)  # Slightly increase brightness
    return image

def crop_and_resize_to_aspect_ratio(image, target_width=1280, target_height=720):
    aspect_ratio = target_width / target_height
    img_width, img_height = image.size
    img_aspect_ratio = img_width / img_height

    if img_aspect_ratio > aspect_ratio:
        new_width = int(img_height * aspect_ratio)
        new_height = img_height
    else:
        new_width = img_width
        new_height = int(img_width / aspect_ratio)

    left = (img_width - new_width) / 2
    top = (img_height - new_height) / 2
    right = (img_width + new_width) / 2
    bottom = (img_height + new_height) / 2

    cropped_image = image.crop((left, top, right, bottom))
    resized_image = cropped_image.resize((target_width, target_height), Image.LANCZOS)
    return resized_image

def create_thumbnail_with_effect(image, output_path, config_path, weights_path, classes_path, irish1_image_path, text="Irish Moments", font_path="D:\One Drive\OneDrive\Business\Youtube\Youtube Maker\Scripts\Thumdnail Maker\Fonts\Bangers-Regular.ttf"):
    print("Creating thumbnail with effect.")
    '''
    box = detect_object(image, config_path, weights_path, classes_path)
    if box:
        image = mask_and_colorize(image, box)
    else:
        print("No objects detected with sufficient confidence. Skipping masking and grayscaling.")
    '''
    image = enhance_image(image)
    image = crop_and_resize_to_aspect_ratio(image)

    draw = ImageDraw.Draw(image)
    try:
        font_size = 120  # Change this value to adjust the font size
        font = ImageFont.truetype(font_path, font_size)  # Adjusted font size
        print(f"Font loaded: {font_path} with size {font_size}")
    except IOError:
        print(f"Font at {font_path} not found. Using default font.")
        font = ImageFont.load_default()

    text_color = "orange"
    text_stroke_color = "black"
    text_stroke_width = 2

    # Calculate the bounding box of the text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_position = ((image.width - text_width) // 2, image.height - text_height - 50)  # Adjusted the vertical position

    draw.text(text_position, text, fill=text_color, font=font, stroke_width=text_stroke_width, stroke_fill=text_stroke_color)

    '''
    # Add the subscribe button image to the top right
    try:
        subscribe_image = Image.open(subscribe_image_path).convert("RGBA")
        subscribe_image = subscribe_image.resize((150, 150), Image.LANCZOS)
        subscribe_position = (image.width - subscribe_image.width - 20, 20)
        image.paste(subscribe_image, subscribe_position, subscribe_image)
        print("Subscribe button added.")
    except Exception as e:
        print(f"Failed to add subscribe button: {e}")
    '''

    # Add the irish image to the top left
    try:
        irish1_image = Image.open(irish1_image_path).convert("RGBA")
        irish1_image = irish1_image.resize((150, 150), Image.LANCZOS)
        irish1_position = (20, 20)
        image.paste(irish1_image, irish1_position, irish1_image)
        print("Irish image added.")
    except Exception as e:
        print(f"Failed to add irish image: {e}")

    image.save(output_path)
    print(f"Thumbnail saved at: {output_path}")

def main(start_label, end_label, video_dir, screenshot_dir, config_path, weights_path, classes_path, irish1_image_path):
    os.makedirs(screenshot_dir, exist_ok=True)

    for label in range(start_label, end_label + 1):
        video_path = os.path.join(video_dir, f"{label}.mp4")
        screenshot_path = os.path.join(screenshot_dir, f"{label}.png")

        print(f"Processing video {video_path}...")

        if os.path.exists(video_path):
            frame = capture_screenshot(video_path, time=20)
            if frame is not None:
                image = Image.fromarray(frame)
                create_thumbnail_with_effect(image, screenshot_path, config_path, weights_path, classes_path, irish1_image_path)
                print(f"Frame extracted and saved to {screenshot_path}")
            else:
                print(f"Failed to capture frame from {video_path}")
        else:
            print(f"Video {video_path} not found")

if __name__ == "__main__":
    start_label = 962
    end_label = 1061
    #video directory will have to be changed
    video_dir = 'M:\Youtube\Vintage Archive\Videos'
    screenshot_dir = 'D:/Test Batch Yt/Thumbnails/1-1000/irish8'
    config_path = 'yolov3.cfg'
    weights_path = 'yolov3.weights'
    classes_path = 'coco.names'
    irish1_image_path = 'D:\One Drive\OneDrive\Business\Youtube\Youtube Maker\Scripts\Thumdnail Maker\Assets\irish4.png'
    main(start_label, end_label, video_dir, screenshot_dir, config_path, weights_path, classes_path, irish1_image_path)
