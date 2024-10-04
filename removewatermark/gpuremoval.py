import cv2
import numpy as np
import argparse
import logging

def remove_watermark(video_path, output_path, template_path, use_gpu=False):
    # Create a VideoCapture object
    cap = cv2.VideoCapture(video_path)
    
    # Check if the video file was opened successfully
    if not cap.isOpened():
        logging.error(f"Error opening video file: {video_path}")
        return
    
    # Get the video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Read the watermark template
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        logging.error(f"Error opening template file: {template_path}")
        return
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Initialize GPU variables
    if use_gpu:
        gpu_frame = cv2.cuda_GpuMat()
        gpu_gray = cv2.cuda_GpuMat()
        gpu_thresh = cv2.cuda_GpuMat()
        gpu_template = cv2.cuda_GpuMat(template)
    
    for frame_num in range(total_frames):
        # Read a frame from the video
        ret, frame = cap.read()
        
        if not ret:
            break
        
        if use_gpu:
            # Upload the frame to GPU
            gpu_frame.upload(frame)
            
            # Convert the frame to grayscale
            cv2.cuda.cvtColor(gpu_frame, cv2.COLOR_BGR2GRAY, gpu_gray)
            
            # Apply adaptive thresholding
            cv2.cuda.adaptiveThreshold(gpu_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2, gpu_thresh)
            
            # Find contours in the thresholded image
            contours, _ = cv2.cuda_GpuMat.findContours(gpu_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Iterate through the contours and remove the watermark
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w)/h
                if aspect_ratio > 5 and w > 100 and h > 10:
                    cv2.cuda.drawContours(gpu_frame, [contour], -1, (0, 0, 0), -1)
            
            # Use template matching to find and remove the watermark
            result = cv2.cuda.matchTemplate(gpu_gray, gpu_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.cuda.minMaxLoc(result)
            if max_val > 0.8:
                x, y = max_loc
                w, h = template.shape[1], template.shape[0]
                cv2.cuda.rectangle(gpu_frame, (x, y), (x+w, y+h), (0, 0, 0), -1)
                cv2.cuda.inpaint(gpu_frame, gpu_thresh, 3, cv2.INPAINT_TELEA)
            
            # Download the modified frame from GPU
            frame = gpu_frame.download()
        
        else:
            # Convert the frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
            
            # Find contours in the thresholded image
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Iterate through the contours and remove the watermark
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w)/h
                if aspect_ratio > 5 and w > 100 and h > 10:
                    cv2.drawContours(frame, [contour], -1, (0, 0, 0), -1)
            
            # Use template matching to find and remove the watermark
            result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if max_val > 0.8:
                x, y = max_loc
                w, h = template.shape[1], template.shape[0]
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 0), -1)
                frame[y:y+h, x:x+w] = cv2.inpaint(frame[y:y+h, x:x+w], thresh[y:y+h, x:x+w], 3, cv2.INPAINT_TELEA)
        
        # Check if the frame is valid before writing to the output video
        if frame is not None:
            out.write(frame)
        else:
            logging.warning(f"Skipping frame {frame_num+1} due to invalid frame data.")
        
        # Display progress
        progress = (frame_num + 1) / total_frames * 100
        print(f"Processing frame {frame_num+1}/{total_frames} ({progress:.2f}%)", end='\r')
    
    # Release the VideoCapture and VideoWriter objects
    cap.release()
    out.release()
    
    print("\nWatermark removal completed.")

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Remove watermark from video')
parser.add_argument('input_video', help='Path to input video file')
parser.add_argument('output_video', help='Path to output video file')
parser.add_argument('template', help='Path to watermark template image')
parser.add_argument('--gpu', action='store_true', help='Use GPU acceleration')
args = parser.parse_args()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Remove watermark from video
remove_watermark(args.input_video, args.output_video, args.template, use_gpu=args.gpu)