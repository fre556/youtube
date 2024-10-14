import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import messagebox, filedialog
from PIL import Image, ImageEnhance, ImageTk, ImageFilter, ImageOps
import os

# Initialize global variable for the image
current_file = None
original_image = None
preview_image = None

def load_image(input_path):
    try:
        img = Image.open(input_path)
        return img
    except Exception as e:
        raise Exception(f"Error loading image: {str(e)}")

def apply_cartoon_effect(img, intensity, alpha):
    # Convert image to grayscale for edge detection
    edges = img.convert('L').filter(ImageFilter.FIND_EDGES)
    edges = ImageOps.invert(edges).convert('RGB')
    
    # Apply smoothing filters to give a more cartoon-like appearance
    for _ in range(intensity):
        img = img.filter(ImageFilter.SMOOTH_MORE)

    # Blend original image with edges to emphasize lines
    img = Image.blend(img, edges, alpha=alpha)
    
    # Apply posterization to reduce the number of colors
    img = img.quantize(colors=32).convert('RGB')
    
    return img

def update_preview():
    global preview_image, original_image
    if original_image is None:
        return

    try:
        # Apply sharpness, brightness, and contrast enhancements
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

        # Update preview image
        img.thumbnail((400, 300), Image.LANCZOS)  # Fit the image to preview window size
        preview_image = ImageTk.PhotoImage(img)
        preview_label.config(image=preview_image)
        preview_label.image = preview_image
    except Exception as e:
        messagebox.showerror("Error", str(e))

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
        sharpness_slider.config(state=tk.NORMAL)
        brightness_slider.config(state=tk.NORMAL)
        contrast_slider.config(state=tk.NORMAL)
        cartoon_slider.config(state=tk.NORMAL)
        cartoon_alpha_slider.config(state=tk.NORMAL)
        resize_checkbox.config(state=tk.NORMAL)
        cartoon_checkbox.config(state=tk.NORMAL)
        download_button.config(state=tk.NORMAL)
        reset_button.config(state=tk.NORMAL)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def download_image():
    try:
        # Get the current enhancements
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

        # Ask user where to save the image
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"),
                                                            ("JPEG files", "*.jpg"),
                                                            ("All files", "*.*")])
        if file_path:
            img.save(file_path)
            messagebox.showinfo("Success", f"Image saved as: {file_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def reset_image():
    global preview_image, original_image
    if original_image is None:
        return

    try:
        # Reset the preview to the original image
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
root.title("Image Enhancer and Resizer Editor")
root.geometry("600x800")

# Create and configure the drop zone
drop_zone = tk.Label(root, text="Drag and drop an image here", bg="lightgrey", height=4)
drop_zone.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

# Create preview label
preview_label = tk.Label(root, text="Image preview will appear here", bg="white", width=400, height=300)
preview_label.pack(pady=10)

# Create sliders frame
sliders_frame = tk.Frame(root)
sliders_frame.pack(pady=10)

# Sharpness slider
sharpness_label = tk.Label(sliders_frame, text="Sharpness")
sharpness_label.grid(row=0, column=0, padx=5, pady=5)
sharpness_slider = tk.Scale(sliders_frame, from_=1, to=10, orient=tk.HORIZONTAL, resolution=0.1, state=tk.DISABLED, command=lambda x: update_preview())
sharpness_slider.set(4.0)
sharpness_slider.grid(row=0, column=1, padx=5, pady=5)

# Brightness slider
brightness_label = tk.Label(sliders_frame, text="Brightness")
brightness_label.grid(row=1, column=0, padx=5, pady=5)
brightness_slider = tk.Scale(sliders_frame, from_=1, to=10, orient=tk.HORIZONTAL, resolution=0.1, state=tk.DISABLED, command=lambda x: update_preview())
brightness_slider.set(1.05)
brightness_slider.grid(row=1, column=1, padx=5, pady=5)

# Contrast slider
contrast_label = tk.Label(sliders_frame, text="Contrast")
contrast_label.grid(row=2, column=0, padx=5, pady=5)
contrast_slider = tk.Scale(sliders_frame, from_=1, to=10, orient=tk.HORIZONTAL, resolution=0.1, state=tk.DISABLED, command=lambda x: update_preview())
contrast_slider.set(1.0)
contrast_slider.grid(row=2, column=1, padx=5, pady=5)

# Cartoon effect intensity slider
cartoon_label = tk.Label(sliders_frame, text="Cartoon Intensity")
cartoon_label.grid(row=3, column=0, padx=5, pady=5)
cartoon_slider = tk.Scale(sliders_frame, from_=1, to=5, orient=tk.HORIZONTAL, state=tk.DISABLED, command=lambda x: update_preview())
cartoon_slider.set(1)
cartoon_slider.grid(row=3, column=1, padx=5, pady=5)

# Cartoon effect alpha blending slider
cartoon_alpha_label = tk.Label(sliders_frame, text="Cartoon Alpha")
cartoon_alpha_label.grid(row=4, column=0, padx=5, pady=5)
cartoon_alpha_slider = tk.Scale(sliders_frame, from_=1, to=10, orient=tk.HORIZONTAL, state=tk.DISABLED, command=lambda x: update_preview())
cartoon_alpha_slider.set(5)
cartoon_alpha_slider.grid(row=4, column=1, padx=5, pady=5)

# Create resize checkbox
resize_var = tk.BooleanVar()
resize_checkbox = tk.Checkbutton(root, text="Resize to 1280x720", variable=resize_var, state=tk.DISABLED, command=update_preview)
resize_checkbox.pack(pady=5)

# Create cartoon effect checkbox
cartoon_var = tk.BooleanVar()
cartoon_checkbox = tk.Checkbutton(root, text="Apply Cartoon Effect", variable=cartoon_var, state=tk.DISABLED, command=update_preview)
cartoon_checkbox.pack(pady=5)

# Create download button
download_button = tk.Button(root, text="Download Image", command=download_image, state=tk.DISABLED)
download_button.pack(pady=5)

# Create reset button
reset_button = tk.Button(root, text="Reset Image", command=reset_image, state=tk.DISABLED)
reset_button.pack(pady=5)

# Create status label
status_label = tk.Label(root, text="No file loaded", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_label.pack(side=tk.BOTTOM, fill=tk.X)

# Enable drag and drop
drop_zone.drop_target_register(DND_FILES)
drop_zone.dnd_bind('<<Drop>>', process_dropped_file)

# Start the GUI event loop
root.mainloop()