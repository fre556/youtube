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

def detect_object(image, config_path, weights_path, classes_path):
    print("Loading YOLO model.")
    net = cv2.dnn.readNet(weights_path, config_path)
    with open(classes_path, 'r') as f:
        classes = f.read().strip().split('\n')
    print(f"Classes loaded: {classes}")

    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

    image_np = np.array(image)
    height, width, channels = image_np.shape
    print(f"Image shape: {image_np.shape}")

    blob = cv2.dnn.blobFromImage(image_np, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
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

    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    indices = list(indices.flatten()) if len(indices) > 0 else []

    print(f"Boxes: {boxes}")
    print(f"Confidences: {confidences}")
    print(f"Indices: {indices}")

    if len(indices) > 0:
        largest_box = boxes[indices[0]]
        print(f"Largest box: {largest_box}")
        return largest_box

    print("No objects detected with sufficient confidence.")
    return None

def mask_and_colorize(image, box):
    print(f"Applying mask and converting to grayscale for box: {box}")
    grayscale_image = ImageOps.grayscale(image)
    mask = Image.new('L', image.size, 0)

    draw = ImageDraw.Draw(mask)
    x, y, w, h = box
    draw.rectangle([x, y, x + w, y + h], fill=255)

    mask = mask.resize(image.size, Image.LANCZOS)
    colorized_object = Image.composite(image, grayscale_image.convert('RGB'), mask)
    return colorized_object

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

def create_thumbnail_with_effect(image, output_path, config_path, weights_path, classes_path, subscribe_image_path, text="Rediscover The Past", font_path="Fonts/BebasNeue-Regular.ttf"):
    print("Creating thumbnail with effect.")
    box = detect_object(image, config_path, weights_path, classes_path)
    if box:
        image = mask_and_colorize(image, box)
    else:
        print("No objects detected with sufficient confidence. Skipping masking and grayscaling.")

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

    text_color = "yellow"
    text_stroke_color = "black"
    text_stroke_width = 2

    # Calculate the bounding box of the text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_position = ((image.width - text_width) // 2, image.height - text_height - 50)  # Adjusted the vertical position

    draw.text(text_position, text, fill=text_color, font=font, stroke_width=text_stroke_width, stroke_fill=text_stroke_color)

    # Add the subscribe button image to the top right
    try:
        subscribe_image = Image.open(subscribe_image_path).convert("RGBA")
        subscribe_image = subscribe_image.resize((300, 300), Image.LANCZOS)
        subscribe_position = (image.width - subscribe_image.width - 20, 20)
        image.paste(subscribe_image, subscribe_position, subscribe_image)
        print("Subscribe button added.")
    except Exception as e:
        print(f"Failed to add subscribe button: {e}")

    image.save(output_path)
    print(f"Thumbnail saved at: {output_path}")

def main(start_label, end_label, video_dir, screenshot_dir, config_path, weights_path, classes_path, subscribe_image_path):
    os.makedirs(screenshot_dir, exist_ok=True)

    for label in range(start_label, end_label + 1):
        video_path = os.path.join(video_dir, f"{label}.mp4")
        screenshot_path = os.path.join(screenshot_dir, f"{label}.png")

        print(f"Processing video {video_path}...")

        if os.path.exists(video_path):
            frame = capture_screenshot(video_path, time=20)
            if frame is not None:
                image = Image.fromarray(frame)
                create_thumbnail_with_effect(image, screenshot_path, config_path, weights_path, classes_path, subscribe_image_path)
                print(f"Frame extracted and saved to {screenshot_path}")
            else:
                print(f"Failed to capture frame from {video_path}")
        else:
            print(f"Video {video_path} not found")

if __name__ == "__main__":
    start_label = 4632
    end_label = 4635
    video_dir = 'TestVideo'
    screenshot_dir = 'screenshots'
    config_path = 'yolov3.cfg'
    weights_path = 'yolov3.weights'
    classes_path = 'coco.names'
    subscribe_image_path = 'Assets/subscribe.png'
    main(start_label, end_label, video_dir, screenshot_dir, config_path, weights_path, classes_path, subscribe_image_path)
