import os
import cv2
from PIL import Image, ImageEnhance, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageChops
import numpy as np

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
    image = enhancer.enhance(1.2)  # Increase contrast
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.2)  # Increase sharpness
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.4)  # Increase brightness
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

def detect_and_colorize_object(frame, config_path, weights_path):
    net = cv2.dnn.readNet(weights_path, config_path)
    layer_names = net.getLayerNames()
    
    try:
        unconnected_out_layers = net.getUnconnectedOutLayers()
        if isinstance(unconnected_out_layers, np.ndarray):
            output_layers = [layer_names[i[0] - 1] for i in unconnected_out_layers]
        else:
            raise ValueError("Unconnected out layers is not an ndarray")
    except Exception as e:
        print(f"Error: {e}")
        print("Using fallback for output layers.")
        output_layers = layer_names[-1:]

    height, width, channels = frame.shape
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    if len(indexes) > 0:
        for i in indexes.flatten():
            x, y, w, h = boxes[i]
            roi_color = frame[y:y + h, x:x + w]
            gray = cv2.cvtColor(roi_color, cv2.COLOR_RGB2GRAY)
            colored_roi = cv2.merge([gray, gray, gray])
            frame[y:y + h, x:x + w] = colored_roi

    return frame

def add_blue_hue(image):
    # Ensure overlay has the same mode and size as the image
    overlay = Image.new('RGB', image.size, '#0000FF')  # Blue hue
    image = image.convert('RGB')
    image = Image.blend(image, overlay, alpha=0.2)
    return image

def add_rounded_border(image, border_color, border_thickness, corner_radius):
    target_width, target_height = image.size
    border = Image.new('RGB', (target_width, target_height + 2 * border_thickness), border_color)
    border.paste(image, (0, border_thickness))

    mask = Image.new('L', (target_width, target_height + 2 * border_thickness), 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle([0, 0, target_width, target_height + 2 * border_thickness], fill=255)
    draw.rounded_rectangle([0, 0, target_width, border_thickness], radius=corner_radius, fill=0)
    draw.rounded_rectangle([0, target_height + border_thickness, target_width, target_height + 2 * border_thickness], radius=corner_radius, fill=0)

    border.putalpha(mask)
    image_with_border = Image.alpha_composite(border.convert('RGBA'), Image.new('RGBA', border.size, (0, 0, 0, 0)))
    return image_with_border.convert('RGB')

def create_thumbnail_with_effect(image, output_path, config_path, weights_path, text="Rediscover The Past", font_path="Berylium.ttf"):
    frame = np.array(image)
    colorized_frame = detect_and_colorize_object(frame, config_path, weights_path)
    image = Image.fromarray(colorized_frame)
    
    image = enhance_image(image)
    image = add_blue_hue(image)

    # Resize and fit the image to the target dimensions
    target_width = 1280
    target_height = 720
    image = ImageOps.fit(image, (target_width, target_height), method=Image.Resampling.LANCZOS)

    # Add gradient to blend edges
    image = add_gradient(image)

    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype(font_path, 80)  # Use Berylium font
    except IOError:
        print(f"Font at {font_path} not found. Using default font.")
        font = ImageFont.load_default()
    
    text_color = "white"
    
    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
    text_position = ((image.width - text_width) // 2, image.height - text_height - 30)
    draw.text(text_position, text, fill=text_color, font=font)
    
    # Add white borders to top and bottom with rounded corners
    border_color = (255, 255, 255)
    border_thickness = 20  # Adjust the border thickness as needed
    corner_radius = 50  # Adjust the corner radius as needed

    bordered_image = add_rounded_border(image, border_color, border_thickness, corner_radius)

    try:
        bordered_image.save(output_path)
        print(f"Thumbnail saved at: {output_path}")
    except Exception as e:
        print(f"Error saving thumbnail: {e}")

def main(start_label, end_label, video_dir, screenshot_dir, config_path, weights_path):
    os.makedirs(screenshot_dir, exist_ok=True)

    for label in range(start_label, end_label + 1):
        video_path = os.path.join(video_dir, f"{label}.mp4")
        screenshot_path = os.path.join(screenshot_dir, f"{label}.png")

        if os.path.exists(video_path):
            frame = capture_screenshot(video_path, time=20)
            if frame is not None:
                image = Image.fromarray(frame)
                create_thumbnail_with_effect(image, screenshot_path, config_path, weights_path)
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
    config_path = "yolov3.cfg"
    weights_path = "yolov3.weights"
    main(start_label, end_label, video_dir, screenshot_dir, config_path, weights_path)
