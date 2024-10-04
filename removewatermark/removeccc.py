import cv2
import numpy as np

def remove_watermark(video_path, output_path):
    # Create a VideoCapture object
    cap = cv2.VideoCapture(video_path)

    # Check if the video file was opened successfully
    if not cap.isOpened():
        print("Error opening video file")
        return

    # Get the video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while True:
        # Read a frame from the video
        ret, frame = cap.read()

        if not ret:
            break

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply a threshold to the grayscale image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Find contours in the thresholded image
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Iterate through the contours and remove the watermark
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w)/h
            if aspect_ratio > 5:
                cv2.drawContours(frame, [contour], -1, (0, 0, 0), -1)

        # Use template matching to find and remove the watermark "ccc"
        template = cv2.imread('template.png')
        result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val > 0.8:
            x, y = max_loc
            w, h = template.shape[1], template.shape[0]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 0), -1)

        # Write the modified frame to the output video
        out.write(frame)

    # Release the VideoCapture and VideoWriter objects
    cap.release()
    out.release()

# Example usage
video_path = 'input.mp4'
output_path = 'output.mp4'
remove_watermark(video_path, output_path)