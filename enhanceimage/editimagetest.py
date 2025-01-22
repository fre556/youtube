import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageEnhance, ImageTk, ImageFilter, ImageOps
import os

# Initialize global variables for the image
current_file = None
original_image = None
preview_image = None

# Function to load an image
def load_image(input_path):
    try:
        img = Image.open(input_path)
        return img
    except Exception as e:
        raise Exception(f"Error loading image: {str(e)}")

# Function to apply cartoon effect
def apply_cartoon_effect(img, intensity, alpha):
    # Convert image to grayscale for edge detection
    edges = img.convert('L').filter(ImageFilter.FIND_EDGES)
    edges = ImageOps.invert(edges).convert('RGB')
    
    # Sharpen edges to make them more defined
    edges = edges.filter(ImageFilter.EDGE_ENHANCE_MORE)

    # Apply a small amount of smoothing to the original image
    img = img.filter(ImageFilter.SMOOTH)

    # Blend original image with edges to emphasize lines
    img = Image.blend(img, edges, alpha=alpha)
    
    # Apply posterization to reduce the number of colors and enhance the cartoon effect
    img = img.quantize(colors=64).convert('RGB')
    
    return img

# Function to update the preview of the image
# Takes into account the zoom level set by the zoom slider
def update_preview():
    global preview_image, original_image
    if original_image is None:
        return

    try:
        # Apply enhancements
        sharpness_factor = sharpness_slider.get()
        brightness_factor = brightness_slider.get()
        contrast_factor = contrast_slider.get()
        cartoon_intensity = cartoon_slider.get()
        cartoon_alpha = cartoon_alpha_slider.get() / 10.0

        img = original_image.copy()
        sharpener = ImageEnhance.Sharpness(img)
        img = sharpener.enhance(sharpness_factor)
        brightener = ImageEnhance.Brightness(img)
        img = brightener.enhance(brightness_factor)
        contrast = ImageEnhance.Contrast(img)
        img = contrast.enhance(contrast_factor)

        # Apply cartoon effect if checkbox is selected
        if cartoon_var.get():
            img = apply_cartoon_effect(img, cartoon_intensity, cartoon_alpha)

        # Resize if checkbox is selected
        if resize_var.get():
            img = img.resize((1280, 720), Image.LANCZOS)

        # Apply zoom based on slider
        zoom_factor = zoom_slider.get()
        new_width = int(img.width * zoom_factor)
        new_height = int(img.height * zoom_factor)
        img = img.resize((new_width, new_height), Image.LANCZOS)

        # Update preview image
        img.thumbnail((400, 300), Image.LANCZOS)
        preview_image = ImageTk.PhotoImage(img)
        preview_label.config(image=preview_image)
        preview_label.image = preview_image
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to handle dropped files
def process_dropped_file(event):
    global current_file, original_image
    file_path = event.data
    if file_path.startswith('{'):
        file_path = file_path[1:-1]
    current_file = file_path
    file_name = os.path.basename(file_path)
    status_label.config(text=f"File loaded: {file_name}")

    try:
        # Load and display the original image
        original_image = load_image(current_file)
        update_preview()
        enable_controls()
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to select an image file
def select_file():
    global current_file, original_image
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"), ("All files", "*.*")])
    if not file_path:
        return
    current_file = file_path
    file_name = os.path.basename(file_path)
    status_label.config(text=f"File loaded: {file_name}")

    try:
        # Load and display the original image
        original_image = load_image(current_file)
        update_preview()
        enable_controls()
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to enable controls once an image is loaded
def enable_controls():
    sharpness_slider.config(state=tk.NORMAL)
    brightness_slider.config(state=tk.NORMAL)
    contrast_slider.config(state=tk.NORMAL)
    cartoon_slider.config(state=tk.NORMAL)
    cartoon_alpha_slider.config(state=tk.NORMAL)
    resize_checkbox.config(state=tk.NORMAL)
    cartoon_checkbox.config(state=tk.NORMAL)
    download_button.config(state=tk.NORMAL)
    reset_button.config(state=tk.NORMAL)

# Function to download the enhanced image
def download_image():
    try:
        sharpness_factor = sharpness_slider.get()
        brightness_factor = brightness_slider.get()
        contrast_factor = contrast_slider.get()
        cartoon_intensity = cartoon_slider.get()
        cartoon_alpha = cartoon_alpha_slider.get() / 10.0

        img = original_image.copy()
        sharpener = ImageEnhance.Sharpness(img)
        img = sharpener.enhance(sharpness_factor)
        brightener = ImageEnhance.Brightness(img)
        img = brightener.enhance(brightness_factor)
        contrast = ImageEnhance.Contrast(img)
        img = contrast.enhance(contrast_factor)

        if cartoon_var.get():
            img = apply_cartoon_effect(img, cartoon_intensity, cartoon_alpha)

        if resize_var.get():
            img = img.resize((1280, 720), Image.LANCZOS)

        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"),
                                                            ("JPEG files", "*.jpg"),
                                                            ("All files", "*.*")])
        if file_path:
            img.save(file_path)
            messagebox.showinfo("Success", f"Image saved as: {file_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to reset the image to the original state
def reset_image():
    global preview_image, original_image
    if original_image is None:
        return

    try:
        preview_image = ImageTk.PhotoImage(original_image.resize((400, 300), Image.LANCZOS))
        preview_label.config(image=preview_image)
        preview_label.image = preview_image
        sharpness_slider.set(1.0)
        brightness_slider.set(1.0)
        contrast_slider.set(1.0)
        cartoon_slider.set(1)
        cartoon_alpha_slider.set(5)
        resize_var.set(False)
        cartoon_var.set(False)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Create the main window using TkinterDnD
root = TkinterDnD.Tk()
root.configure(bg='#f0f0f0')
root.title("Image Enhancer and Resizer Editor")
root.geometry("700x850")
root.resizable(True, True)

# File selection button
select_file_button = ttk.Button(root, text="Select Image File", command=select_file)
select_file_button.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

# Drag and drop area
drop_zone = tk.Label(root, text="Or drag and drop an image here", bg='#dfe3e6', fg='#333', anchor='center', padx=10, pady=10, font=('Arial', 12, 'bold'))
drop_zone.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)
drop_zone.drop_target_register(DND_FILES)
drop_zone.dnd_bind('<<Drop>>', process_dropped_file)

# Image preview area
preview_frame = tk.LabelFrame(root, text="Image Preview", padx=10, pady=10, bg='#f0f0f0', font=('Arial', 12, 'bold'), fg='#333')
preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Zoom control frame
zoom_frame = tk.Frame(preview_frame, bg='#f0f0f0')
zoom_frame.pack(fill=tk.X, padx=5, pady=5)
zoom_label = ttk.Label(zoom_frame, text="Zoom", background='#f0f0f0', font=('Arial', 10))
zoom_label.pack(side=tk.LEFT)
zoom_slider = ttk.Scale(zoom_frame, from_=1, to=5, orient=tk.HORIZONTAL, command=lambda x: update_preview())
zoom_slider.set(1.0)
zoom_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

# Preview label
preview_label = ttk.Label(preview_frame, text="Image preview will appear here", anchor="center")
preview_label.pack(fill=tk.BOTH, expand=True)

# Adjustments area
sliders_frame = tk.LabelFrame(root, text="Adjustments", padx=10, pady=10, bg='#f0f0f0', font=('Arial', 12, 'bold'), fg='#333')
sliders_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

# Sharpness slider
sharpness_label = ttk.Label(sliders_frame, text="Sharpness", background='#f0f0f0', font=('Arial', 10))
sharpness_label.grid(row=0, column=0, padx=5, pady=5)
sharpness_slider = ttk.Scale(sliders_frame, from_=1, to=10, orient=tk.HORIZONTAL, command=lambda x: update_preview())
sharpness_slider.set(4.0)
sharpness_slider.state(['disabled'])
sharpness_slider.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# Brightness slider
brightness_label = ttk.Label(sliders_frame, text="Brightness", background='#f0f0f0', font=('Arial', 10))
brightness_label.grid(row=1, column=0, padx=5, pady=5)
brightness_slider = ttk.Scale(sliders_frame, from_=1, to=10, orient=tk.HORIZONTAL, command=lambda x: update_preview())
brightness_slider.set(1.05)
brightness_slider.state(['disabled'])
brightness_slider.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

# Contrast slider
contrast_label = ttk.Label(sliders_frame, text="Contrast", background='#f0f0f0', font=('Arial', 10))
contrast_label.grid(row=2, column=0, padx=5, pady=5)
contrast_slider = ttk.Scale(sliders_frame, from_=1, to=10, orient=tk.HORIZONTAL, command=lambda x: update_preview())
contrast_slider.set(1.0)
contrast_slider.state(['disabled'])
contrast_slider.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

# Cartoon effect intensity slider
cartoon_label = ttk.Label(sliders_frame, text="Cartoon Intensity", background='#f0f0f0', font=('Arial', 10))
cartoon_label.grid(row=3, column=0, padx=5, pady=5)
cartoon_slider = ttk.Scale(sliders_frame, from_=1, to=5, orient=tk.HORIZONTAL, command=lambda x: update_preview())
cartoon_slider.set(1)
cartoon_slider.state(['disabled'])
cartoon_slider.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

# Cartoon effect alpha blending slider
cartoon_alpha_label = ttk.Label(sliders_frame, text="Cartoon Alpha", background='#f0f0f0', font=('Arial', 10))
cartoon_alpha_label.grid(row=4, column=0, padx=5, pady=5)
cartoon_alpha_slider = ttk.Scale(sliders_frame, from_=1, to=10, orient=tk.HORIZONTAL, command=lambda x: update_preview())
cartoon_alpha_slider.set(5)
cartoon_alpha_slider.state(['disabled'])
cartoon_alpha_slider.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

# Resize checkbox
resize_var = tk.BooleanVar()
resize_checkbox = ttk.Checkbutton(root, text="Resize to 1280x720", variable=resize_var, command=update_preview, state="disabled")
resize_checkbox.pack(pady=5)

# Cartoon effect checkbox
cartoon_var = tk.BooleanVar()
cartoon_checkbox = ttk.Checkbutton(root, text="Apply Cartoon Effect", variable=cartoon_var, command=update_preview, state="disabled")
cartoon_checkbox.pack(pady=5)

# Buttons frame
buttons_frame = tk.Frame(root, bg='#f0f0f0')
buttons_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

# Download button
download_button = ttk.Button(buttons_frame, text="Download Image", command=download_image, state="disabled")
download_button.pack(side=tk.LEFT, expand=True, padx=5, pady=5)

# Reset button
reset_button = ttk.Button(buttons_frame, text="Reset Image", command=reset_image, state="disabled")
reset_button.pack(side=tk.LEFT, expand=True, padx=5, pady=5)

# Status label
status_label = tk.Label(root, text="No file loaded", relief=tk.SUNKEN, anchor=tk.W, bg='#dfe3e6', fg='#333', font=('Arial', 10))
status_label.pack(side=tk.BOTTOM, fill=tk.X)

# Start the GUI event loop
root.mainloop()