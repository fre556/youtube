import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import messagebox
from PIL import Image, ImageEnhance
import os

def enhance_image(input_path):
    try:
        img = Image.open(input_path)
        sharpener = ImageEnhance.Sharpness(img)
        img = sharpener.enhance(4.0)
        brightener = ImageEnhance.Brightness(img)
        img = brightener.enhance(1.05)
        filename, ext = os.path.splitext(input_path)
        output_path = f"{filename}_enhanced{ext}"
        img.save(output_path)
        return output_path
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")

def resize_image(input_path):
    try:
        img = Image.open(input_path)
        img = img.resize((1280, 720), Image.LANCZOS)
        filename, ext = os.path.splitext(input_path)
        output_path = f"{filename}_resized{ext}"
        img.save(output_path)
        return output_path
    except Exception as e:
        raise Exception(f"Error resizing image: {str(e)}")

def process_dropped_file(event):
    global current_file
    file_path = event.data
    if file_path.startswith('{'):
        file_path = file_path[1:-1]
    current_file = file_path
    file_name = os.path.basename(file_path)
    status_label.config(text=f"File loaded: {file_name}")
    enhance_button.config(state=tk.NORMAL)
    resize_button.config(state=tk.NORMAL)

def enhance_current_file():
    try:
        output_path = enhance_image(current_file)
        messagebox.showinfo("Success", f"Image enhanced and saved as:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def resize_current_file():
    try:
        output_path = resize_image(current_file)
        messagebox.showinfo("Success", f"Image resized and saved as:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Create the main window using TkinterDnD
root = TkinterDnD.Tk()
root.title("Image Enhancer and Resizer")
root.geometry("400x300")

# Create and configure the drop zone
drop_zone = tk.Label(root, text="Drag and drop an image here", bg="lightgrey", height=8)
drop_zone.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Create status label
status_label = tk.Label(root, text="No file loaded", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_label.pack(side=tk.BOTTOM, fill=tk.X)

# Create button frame
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Create enhance button
enhance_button = tk.Button(button_frame, text="Enhance Image", command=enhance_current_file, state=tk.DISABLED)
enhance_button.pack(side=tk.LEFT, padx=5)

# Create resize button
resize_button = tk.Button(button_frame, text="Resize to 1280x720", command=resize_current_file, state=tk.DISABLED)
resize_button.pack(side=tk.LEFT, padx=5)

# Enable drag and drop
drop_zone.drop_target_register(DND_FILES)
drop_zone.dnd_bind('<<Drop>>', process_dropped_file)

# Initialize global variable for current file
current_file = None

# Start the GUI event loop
root.mainloop()