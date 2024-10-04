from PIL import Image

# Load the image
image_path = "vintagearchive.png"
output_path = "vintagearchive_white.png"

# Open the image
image = Image.open(image_path).convert("RGBA")

# Load pixel data
pixels = image.load()

# Create a new image with the same size and white background
new_image = Image.new("RGBA", image.size, (255, 255, 255, 0))
new_pixels = new_image.load()

# Iterate over each pixel
for y in range(image.size[1]):
    for x in range(image.size[0]):
        r, g, b, a = pixels[x, y]
        
        # Change black to white
        if (r, g, b) == (0, 0, 0):
            new_pixels[x, y] = (255, 255, 255, a)
        else:
            new_pixels[x, y] = (r, g, b, a)

# Save the new image
new_image.save(output_path)

output_path
