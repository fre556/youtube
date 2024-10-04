from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageChops
import os

def enhance_image(image):
    # Enhance the contrast, sharpness, and brightness
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(2)
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.8)  # Increase brightness
    return image

def add_sunset_hue(image):
    # Apply an orange/sunset hue to the image
    overlay = Image.new('RGB', image.size, '#FF4500')  # Sunset hue
    image = Image.blend(image, overlay, alpha=0.3)
    return image

def adjust_image_properties(image):
    # Adjust contrast, brightness, and add blur for the modern twist
    image = ImageEnhance.Contrast(image).enhance(1.5)
    image = ImageEnhance.Brightness(image).enhance(1.3)
    image = image.filter(ImageFilter.GaussianBlur(1))
    return image

def create_gradient(width, height):
    gradient = Image.new('L', (width, height), color=0xFF)
    for x in range(width):
        for y in range(height):
            gradient.putpixel((x, y), int(255 * (1 - x / width)))
    return gradient

def add_cloud_overlay(image, cloud_overlay_path):
    try:
        cloud_overlay = Image.open(cloud_overlay_path).convert("RGBA")
        
        # Remove green background
        r, g, b, a = cloud_overlay.split()
        green_background = Image.new('RGBA', cloud_overlay.size, (0, 255, 0, 0))
        cloud_overlay = ImageChops.subtract(cloud_overlay, green_background)
        
        # Resize cloud overlay to match the image size
        cloud_overlay = cloud_overlay.resize(image.size, Image.Resampling.LANCZOS)
        cloud_overlay = cloud_overlay.putalpha(128)  # Adjust alpha for transparency

        image = Image.alpha_composite(image.convert("RGBA"), cloud_overlay)
    except Exception as e:
        print(f"Error adding cloud overlay: {e}")
    return image

def create_thumbnail_with_effect(image1_path, image2_path, output_path, text="PAST IN COLOR", subtitle="— A Journey Through Time —", font_path="Berylium.ttf", cloud_overlay_path=None):
    # Check if the image paths are correct
    if not os.path.exists(image1_path):
        print(f"Error: The file {image1_path} does not exist.")
        return
    if not os.path.exists(image2_path):
        print(f"Error: The file {image2_path} does not exist.")
        return
    if not os.path.exists(font_path):
        print(f"Error: The font file {font_path} does not exist.")
        return

    # Load the images
    try:
        image1 = Image.open(image1_path)
        image2 = Image.open(image2_path)
    except Exception as e:
        print(f"Error loading images: {e}")
        return

    # Enhance the first image
    image1 = enhance_image(image1)

    # Apply an orange/sunset hue to the second image and adjust properties
    image2 = add_sunset_hue(image2)
    image2 = adjust_image_properties(image2)
    
    # Resize images to ensure they are the same height
    target_height = 800
    image1 = image1.resize((int(image1.width * (target_height / image1.height)), target_height), Image.Resampling.LANCZOS)
    image2 = image2.resize((int(image2.width * (target_height / image2.height)), target_height), Image.Resampling.LANCZOS)
    
    # Create a blank canvas
    thumbnail_width = image1.width + image2.width
    thumbnail_height = target_height
    thumbnail = Image.new('RGB', (thumbnail_width, thumbnail_height), color=(255, 255, 255))
    
    # Paste images onto the canvas
    thumbnail.paste(image1.convert("RGB"), (0, 0))
    thumbnail.paste(image2, (image1.width, 0))
    
    # Add the gradient effect for a smoother transition
    gradient = create_gradient(200, target_height)
    alpha_gradient = gradient.convert('L')
    gradient_image = Image.new('RGBA', (thumbnail_width, thumbnail_height), (0, 0, 0, 0))
    gradient_image.paste((0, 0, 0, 255), (image1.width - 100, 0, image1.width + 100, target_height))
    alpha_gradient = alpha_gradient.resize((thumbnail_width, thumbnail_height), Image.Resampling.LANCZOS)
    gradient_image.putalpha(alpha_gradient)
    thumbnail = Image.alpha_composite(thumbnail.convert('RGBA'), gradient_image)
    
    # Optionally add cloud overlay
    if cloud_overlay_path:
        thumbnail = add_cloud_overlay(thumbnail, cloud_overlay_path)
    
    # Draw text and decorative elements
    draw = ImageDraw.Draw(thumbnail)
    
    # Use the custom font
    try:
        font = ImageFont.truetype(font_path, 100)  # Increased font size
        subtitle_font = ImageFont.truetype(font_path, 50)  # Increased subtitle font size
    except IOError:
        print(f"Font at {font_path} not found. Using default font.")
        font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Draw main text
    text_width, text_height = draw.textsize(text, font=font)
    text_position = ((thumbnail_width - text_width) // 2, thumbnail_height // 2 - text_height - 20)
    draw.text(text_position, text, fill="white", font=font)
    
    # Draw subtitle
    subtitle_width, subtitle_height = draw.textsize(subtitle, font=subtitle_font)
    subtitle_position = ((thumbnail_width - subtitle_width) // 2, thumbnail_height // 2 + 50)
    draw.text(subtitle_position, subtitle, fill="white", font=subtitle_font)
    
    # Add decorative lines (optional)
    line_thickness = 4
    line_color = (255, 255, 255)
    draw.line((0, 0, thumbnail_width, 0), fill=line_color, width=line_thickness)
    draw.line((0, thumbnail_height - line_thickness, thumbnail_width, thumbnail_height - line_thickness), fill=line_color, width=line_thickness)
    draw.line((0, 0, 0, thumbnail_height), fill=line_color, width=line_thickness)
    draw.line((thumbnail_width - line_thickness, 0, thumbnail_width - line_thickness, thumbnail_height), fill=line_color, width=line_thickness)
    
    # Save the thumbnail
    try:
        thumbnail.save(output_path)
        print(f"Thumbnail saved at: {output_path}")
    except Exception as e:
        print(f"Error saving thumbnail: {e}")

# Paths to your images and output
image1_path = "image1.jpg"  # Replace with the actual filename of the first image
image2_path = "image2.jpg"  # Replace with the actual filename of the second image
output_path = "thumbnail_with_effect.png"
cloud_overlay_path = "clouds.png"  # Replace with the actual filename of the cloud overlay image

# Create the thumbnail with effect
create_thumbnail_with_effect(image1_path, image2_path, output_path, text="PAST IN COLOR", subtitle="— A Journey Through Time —", font_path="Berylium.ttf", cloud_overlay_path=cloud_overlay_path)
