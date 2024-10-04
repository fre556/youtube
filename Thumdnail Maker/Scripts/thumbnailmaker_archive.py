import os
import cv2
from PIL import Image, ImageEnhance, ImageDraw, ImageFont, ImageFilter, ImageOps

def capture_screenshot(video_path, time=20):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_number = int(fps * time)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    success, frame = cap.read()
    if success:
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    else:
        return None

def enhance_image(image):
    # Convert to grayscale
    image = image.convert('L')
    # Enhance the contrast, sharpness, and brightness
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)  # Increase contrast
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(2.0)  # Increase sharpness
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.0)  # Slightly increase brightness
    return image

def add_gradient(image, direction='horizontal'):
    width, height = image.size
    gradient = Image.new('L', (width, height), color=0xFF)

    for x in range(width):
        for y in range(height):
            if direction == 'horizontal':
                gradient.putpixel((x, y), int(255 * (1 - x / width)))
            else:
                gradient.putpixel((x, y), int(255 * (1 - y / height)))

    alpha_gradient = gradient.convert('L')
    gradient_image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    gradient_image.putalpha(alpha_gradient)
    
    return Image.alpha_composite(image.convert('RGBA'), gradient_image)

def create_thumbnail_with_effect(image, output_path, text="Rediscover The Past", font_path="Berylium.ttf"):
    image = enhance_image(image)

    # Resize and fit the image to the target dimensions
    target_width = 1280
    target_height = 720
    image = ImageOps.fit(image, (target_width, target_height), method=Image.Resampling.LANCZOS)

    # Add gradient to blend edges
    image = add_gradient(image, direction='horizontal')

    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype(font_path, 150)  # Increased font size
    except IOError:
        print(f"Font at {font_path} not found. Using default font.")
        font = ImageFont.load_default()
    
    text_color = "white"
    text_stroke_color = "black"
    
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
    text_position = ((image.width - text_width) // 2, image.height - text_height - 50)
    
    # Draw text with border (stroke)
    draw.text(text_position, text, font=font, fill=text_color, stroke_width=2, stroke_fill=text_stroke_color)
    
    try:
        image.save(output_path)
        print(f"Thumbnail saved at: {output_path}")
    except Exception as e:
        print(f"Error saving thumbnail: {e}")

def main(start_label, end_label, video_dir, screenshot_dir):
    os.makedirs(screenshot_dir, exist_ok=True)

    for label in range(start_label, end_label + 1):
        video_path = os.path.join(video_dir, f"{label}.mp4")
        screenshot_path = os.path.join(screenshot_dir, f"{label}.png")

        if os.path.exists(video_path):
            frame = capture_screenshot(video_path, time=20)
            if frame is not None:
                image = Image.fromarray(frame)
                create_thumbnail_with_effect(image, screenshot_path)
                print(f"Frame extracted and saved to {screenshot_path}")
            else:
                print(f"Failed to capture frame from {video_path}")
        else:
            print(f"Video {video_path} not found")

if __name__ == "__main__":
    start_label = 3286
    end_label = 3289
    video_dir = 'TestVideo'
    screenshot_dir = 'screenshots'
    main(start_label, end_label, video_dir, screenshot_dir)
